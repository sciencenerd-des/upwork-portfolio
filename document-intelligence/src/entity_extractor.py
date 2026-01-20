"""
Entity Extraction Module

Extracts named entities using spaCy NER and regex patterns.
- Dates (multiple formats)
- Amounts (INR, USD, EUR)
- Persons (spaCy PERSON)
- Organizations (spaCy ORG)
- Custom patterns (invoice #, GSTIN, PAN, email, phone)
"""

import re
import logging
from datetime import datetime
from typing import Optional
from collections import defaultdict

from app.config import get_settings
from app.models import (
    ExtractedEntities,
    ExtractedEntity,
    AmountEntity,
    DateEntity,
    EntityType,
)

logger = logging.getLogger(__name__)

# Try to import spaCy
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logger.warning("spaCy not available. Using regex-only extraction.")


class EntityExtractor:
    """
    Extracts entities from text using spaCy NER and regex patterns.
    """

    def __init__(self):
        self.settings = get_settings()
        self._confidence_threshold = self.settings.entity_extraction.confidence_threshold
        self._deduplicate = self.settings.entity_extraction.deduplicate
        self._patterns = self.settings.entity_extraction.patterns

        # Load spaCy model
        self._nlp = None
        if SPACY_AVAILABLE:
            self._load_spacy_model()

        # Compile regex patterns
        self._compiled_patterns = self._compile_patterns()

    def _load_spacy_model(self) -> None:
        """Load spaCy model for NER."""
        try:
            model_name = self.settings.entity_extraction.spacy_model
            self._nlp = spacy.load(model_name)
            logger.info(f"Loaded spaCy model: {model_name}")
        except OSError:
            try:
                self._nlp = spacy.load("en_core_web_sm")
                logger.info("Loaded fallback spaCy model: en_core_web_sm")
            except OSError:
                logger.warning("No spaCy model available.")
                self._nlp = None

    def _compile_patterns(self) -> dict:
        """Compile regex patterns from config."""
        compiled = {}

        # Date patterns
        compiled["date"] = [
            # MM/DD/YYYY or DD/MM/YYYY
            re.compile(r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b'),
            # YYYY-MM-DD (ISO format)
            re.compile(r'\b(\d{4}[-/]\d{2}[-/]\d{2})\b'),
            # Month DD, YYYY
            re.compile(r'\b(\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4})\b', re.I),
            # DD Month YYYY
            re.compile(r'\b((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+\d{4})\b', re.I),
        ]

        # Amount patterns
        compiled["amount_inr"] = [
            re.compile(r'(?:₹|Rs\.?|INR)\s*([\d,]+(?:\.\d{2})?)', re.I),
            re.compile(r'([\d,]+(?:\.\d{2})?)\s*(?:₹|Rs\.?|INR)', re.I),
        ]
        compiled["amount_usd"] = [
            re.compile(r'(?:\$|USD)\s*([\d,]+(?:\.\d{2})?)', re.I),
            re.compile(r'([\d,]+(?:\.\d{2})?)\s*(?:\$|USD)', re.I),
        ]
        compiled["amount_eur"] = [
            re.compile(r'(?:€|EUR)\s*([\d,]+(?:\.\d{2})?)', re.I),
            re.compile(r'([\d,]+(?:\.\d{2})?)\s*(?:€|EUR)', re.I),
        ]

        # Indian tax identifiers
        compiled["gstin"] = [
            re.compile(r'\b(\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1})\b'),
        ]
        compiled["pan"] = [
            re.compile(r'\b([A-Z]{5}\d{4}[A-Z]{1})\b'),
        ]

        # Invoice/reference numbers
        compiled["invoice_number"] = [
            re.compile(r'(?:Invoice|Inv|Bill)\s*(?:#|No\.?|Number)?\s*:?\s*([A-Z0-9][-A-Z0-9/]+)', re.I),
            re.compile(r'(?:#|No\.?)\s*:?\s*([A-Z]{2,3}[-/]?\d{4,})', re.I),
        ]

        # Contact information
        compiled["email"] = [
            re.compile(r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'),
        ]
        compiled["phone"] = [
            re.compile(r'\b(\+?[\d\s()-]{10,15})\b'),
            re.compile(r'\b(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})\b'),  # US format
            re.compile(r'\b(\d{5}[-.\s]?\d{5})\b'),  # Indian mobile
        ]

        return compiled

    # =========================================================================
    # Main Extraction
    # =========================================================================

    def extract(self, text: str) -> ExtractedEntities:
        """
        Extract all entities from text.

        Args:
            text: Text to extract entities from

        Returns:
            ExtractedEntities with all found entities
        """
        if not text.strip():
            return ExtractedEntities()

        entities = ExtractedEntities()

        # Extract with spaCy if available
        if self._nlp:
            spacy_entities = self._extract_with_spacy(text)
            entities.persons.extend(spacy_entities.get("persons", []))
            entities.organizations.extend(spacy_entities.get("organizations", []))

        # Extract with regex patterns
        entities.dates.extend(self._extract_dates(text))
        entities.amounts.extend(self._extract_amounts(text))
        entities.emails.extend(self._extract_emails(text))
        entities.phones.extend(self._extract_phones(text))
        entities.invoice_numbers.extend(self._extract_invoice_numbers(text))
        entities.gstins.extend(self._extract_gstins(text))
        entities.pans.extend(self._extract_pans(text))

        # Deduplicate if enabled
        if self._deduplicate:
            entities = self._deduplicate_entities(entities)

        return entities

    def _extract_with_spacy(self, text: str) -> dict:
        """Extract entities using spaCy NER."""
        entities = {"persons": [], "organizations": []}

        try:
            # Process in chunks for large texts
            max_length = 100000
            for i in range(0, len(text), max_length):
                chunk = text[i:i + max_length]
                doc = self._nlp(chunk)

                for ent in doc.ents:
                    if ent.label_ == "PERSON":
                        entities["persons"].append(ExtractedEntity(
                            entity_type=EntityType.PERSON,
                            value=ent.text.strip(),
                            confidence=0.85,  # spaCy doesn't provide confidence, use default
                            position={"start": ent.start_char + i, "end": ent.end_char + i}
                        ))
                    elif ent.label_ == "ORG":
                        entities["organizations"].append(ExtractedEntity(
                            entity_type=EntityType.ORGANIZATION,
                            value=ent.text.strip(),
                            confidence=0.85,
                            position={"start": ent.start_char + i, "end": ent.end_char + i}
                        ))

        except Exception as e:
            logger.error(f"spaCy extraction error: {e}")

        return entities

    # =========================================================================
    # Pattern-based Extraction
    # =========================================================================

    def _extract_dates(self, text: str) -> list[DateEntity]:
        """Extract dates using regex patterns."""
        dates = []

        for pattern in self._compiled_patterns.get("date", []):
            for match in pattern.finditer(text):
                date_str = match.group(1)
                parsed = self._parse_date(date_str)

                dates.append(DateEntity(
                    value=date_str,
                    parsed_date=parsed,
                    confidence=0.9 if parsed else 0.7,
                    position={"start": match.start(), "end": match.end()}
                ))

        return dates

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Try to parse date string into datetime."""
        formats = [
            "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y",
            "%d %B %Y", "%B %d, %Y", "%d %b %Y", "%b %d, %Y",
            "%d/%m/%y", "%m/%d/%y"
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None

    def _extract_amounts(self, text: str) -> list[AmountEntity]:
        """Extract monetary amounts."""
        amounts = []

        # INR amounts
        for pattern in self._compiled_patterns.get("amount_inr", []):
            for match in pattern.finditer(text):
                value = match.group(1).replace(",", "")
                amounts.append(AmountEntity(
                    value=match.group(0),
                    numeric_value=self._parse_amount(value),
                    currency="INR",
                    confidence=0.95,
                    position={"start": match.start(), "end": match.end()}
                ))

        # USD amounts
        for pattern in self._compiled_patterns.get("amount_usd", []):
            for match in pattern.finditer(text):
                value = match.group(1).replace(",", "")
                amounts.append(AmountEntity(
                    value=match.group(0),
                    numeric_value=self._parse_amount(value),
                    currency="USD",
                    confidence=0.95,
                    position={"start": match.start(), "end": match.end()}
                ))

        # EUR amounts
        for pattern in self._compiled_patterns.get("amount_eur", []):
            for match in pattern.finditer(text):
                value = match.group(1).replace(",", "")
                amounts.append(AmountEntity(
                    value=match.group(0),
                    numeric_value=self._parse_amount(value),
                    currency="EUR",
                    confidence=0.95,
                    position={"start": match.start(), "end": match.end()}
                ))

        return amounts

    def _parse_amount(self, value: str) -> Optional[float]:
        """Parse amount string to float."""
        try:
            return float(value.replace(",", ""))
        except ValueError:
            return None

    def _extract_emails(self, text: str) -> list[ExtractedEntity]:
        """Extract email addresses."""
        emails = []

        for pattern in self._compiled_patterns.get("email", []):
            for match in pattern.finditer(text):
                emails.append(ExtractedEntity(
                    entity_type=EntityType.EMAIL,
                    value=match.group(1),
                    confidence=0.98,
                    position={"start": match.start(), "end": match.end()}
                ))

        return emails

    def _extract_phones(self, text: str) -> list[ExtractedEntity]:
        """Extract phone numbers."""
        phones = []

        for pattern in self._compiled_patterns.get("phone", []):
            for match in pattern.finditer(text):
                # Clean up phone number
                phone = re.sub(r'[^\d+]', '', match.group(1))
                if len(phone) >= 10:  # Valid phone length
                    phones.append(ExtractedEntity(
                        entity_type=EntityType.PHONE,
                        value=match.group(1).strip(),
                        confidence=0.85,
                        position={"start": match.start(), "end": match.end()}
                    ))

        return phones

    def _extract_invoice_numbers(self, text: str) -> list[ExtractedEntity]:
        """Extract invoice/reference numbers."""
        invoices = []

        for pattern in self._compiled_patterns.get("invoice_number", []):
            for match in pattern.finditer(text):
                invoices.append(ExtractedEntity(
                    entity_type=EntityType.INVOICE_NUMBER,
                    value=match.group(1),
                    label="Invoice Number",
                    confidence=0.9,
                    position={"start": match.start(), "end": match.end()}
                ))

        return invoices

    def _extract_gstins(self, text: str) -> list[ExtractedEntity]:
        """Extract Indian GSTIN numbers."""
        gstins = []

        for pattern in self._compiled_patterns.get("gstin", []):
            for match in pattern.finditer(text):
                gstin = match.group(1)
                if self._validate_gstin(gstin):
                    gstins.append(ExtractedEntity(
                        entity_type=EntityType.GSTIN,
                        value=gstin,
                        label="GSTIN",
                        confidence=0.98,
                        position={"start": match.start(), "end": match.end()}
                    ))

        return gstins

    def _validate_gstin(self, gstin: str) -> bool:
        """Validate GSTIN format."""
        if len(gstin) != 15:
            return False
        # Basic format validation (could add checksum validation)
        return bool(re.match(r'^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}Z[A-Z\d]{1}$', gstin))

    def _extract_pans(self, text: str) -> list[ExtractedEntity]:
        """Extract Indian PAN numbers."""
        pans = []

        for pattern in self._compiled_patterns.get("pan", []):
            for match in pattern.finditer(text):
                pan = match.group(1)
                if self._validate_pan(pan):
                    pans.append(ExtractedEntity(
                        entity_type=EntityType.PAN,
                        value=pan,
                        label="PAN",
                        confidence=0.95,
                        position={"start": match.start(), "end": match.end()}
                    ))

        return pans

    def _validate_pan(self, pan: str) -> bool:
        """Validate PAN format."""
        if len(pan) != 10:
            return False
        return bool(re.match(r'^[A-Z]{5}\d{4}[A-Z]$', pan))

    # =========================================================================
    # Deduplication
    # =========================================================================

    def _deduplicate_entities(self, entities: ExtractedEntities) -> ExtractedEntities:
        """Remove duplicate entities, keeping highest confidence."""

        def dedupe_list(items: list) -> list:
            seen = {}
            for item in items:
                key = item.value.lower().strip()
                if key not in seen or item.confidence > seen[key].confidence:
                    seen[key] = item
            return list(seen.values())

        return ExtractedEntities(
            dates=dedupe_list(entities.dates),
            amounts=dedupe_list(entities.amounts),
            persons=dedupe_list(entities.persons),
            organizations=dedupe_list(entities.organizations),
            emails=dedupe_list(entities.emails),
            phones=dedupe_list(entities.phones),
            invoice_numbers=dedupe_list(entities.invoice_numbers),
            gstins=dedupe_list(entities.gstins),
            pans=dedupe_list(entities.pans),
            custom=dedupe_list(entities.custom),
        )


# Singleton instance
_entity_extractor: Optional[EntityExtractor] = None


def get_entity_extractor() -> EntityExtractor:
    """Get or create entity extractor instance."""
    global _entity_extractor
    if _entity_extractor is None:
        _entity_extractor = EntityExtractor()
    return _entity_extractor
