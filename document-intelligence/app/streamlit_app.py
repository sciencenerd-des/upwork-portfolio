"""
Streamlit UI for Document Intelligence System

Interactive web interface for:
- Document upload and processing
- Summary and key points display
- Entity extraction visualization
- RAG-based Q&A chat
- Export functionality

Modern light-themed UI inspired by Mixpanel, Claude, MindMarket, ClickUp
"""

import io
import time
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_settings
from app.models import DocumentStatus, ExportFormat
from src.document_store import get_document_store
from src.document_loader import get_document_loader
from src.ocr_engine import get_ocr_engine
from src.text_processor import get_text_processor
from src.entity_extractor import get_entity_extractor
from src.vector_store import get_document_vector_store
from src.summarizer import get_summarizer
from src.qa_engine import get_qa_engine
from src.exporter import get_exporter

# Page configuration - no sidebar
st.set_page_config(
    page_title="Document Intelligence",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================================
# CSS LOADING
# ============================================================================

def load_css():
    """Load CSS from external file."""
    css_path = Path(__file__).parent / "assets" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

load_css()


# ============================================================================
# SVG ICONS
# ============================================================================

ICONS = {
    "document": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14,2 14,8 20,8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg>',
    "sparkles": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/></svg>',
    "upload": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17,8 12,3 7,8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>',
    "file-text": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg>',
    "list": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>',
    "message-circle": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z"/></svg>',
    "download": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>',
    "check": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    "zap": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    "search": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>',
    "layers": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/></svg>',
}


def get_icon(name: str, size: int = 24) -> str:
    """Get SVG icon by name."""
    icon = ICONS.get(name, ICONS["document"])
    return icon.replace('width="24"', f'width="{size}"').replace('height="24"', f'height="{size}"')


# ============================================================================
# HTML RENDERING HELPERS
# ============================================================================

def render_html(html: str) -> None:
    """Render HTML block safely."""
    cleaned = "\n".join(line.lstrip() for line in html.splitlines()).strip()
    st.markdown(cleaned, unsafe_allow_html=True)


def render_animated_background():
    """Render the animated geometric background with scroll-speed responsive elements."""
    render_html("""
    <div class="animated-bg" id="animatedBg">
        <!-- SVG Canvas for all shapes -->
        <svg class="geo-canvas" viewBox="0 0 1920 2000" preserveAspectRatio="xMidYMid slice">
            <defs>
                <!-- Gradients -->
                <linearGradient id="curveGrad1" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stop-color="#d97706" stop-opacity="0.7"/>
                    <stop offset="50%" stop-color="#ea580c" stop-opacity="0.9"/>
                    <stop offset="100%" stop-color="#f59e0b" stop-opacity="0.5"/>
                </linearGradient>
                <linearGradient id="curveGrad2" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stop-color="#f59e0b" stop-opacity="0.6"/>
                    <stop offset="100%" stop-color="#d97706" stop-opacity="0.8"/>
                </linearGradient>
                <linearGradient id="moleculeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#d97706" stop-opacity="0.8"/>
                    <stop offset="100%" stop-color="#ea580c" stop-opacity="0.6"/>
                </linearGradient>
            </defs>
            
            <!-- ===== CURVED FLOWING LINES ===== -->
            <g class="curves-group">
                <!-- Primary flowing curves -->
                <path class="scroll-curve" data-speed="0.15" data-direction="1"
                      d="M-200,120 Q200,40 500,180 T1000,80 T1500,200 T2000,100 T2500,180" 
                      stroke="url(#curveGrad1)" stroke-width="3.5" fill="none" stroke-linecap="round"/>
                <path class="scroll-curve" data-speed="0.2" data-direction="-1"
                      d="M-100,280 Q300,180 600,320 T1100,220 T1600,360 T2100,260" 
                      stroke="url(#curveGrad2)" stroke-width="3" fill="none" stroke-linecap="round"/>
                <path class="scroll-curve" data-speed="0.12" data-direction="1"
                      d="M0,450 Q400,350 800,500 T1400,400 T2000,550" 
                      stroke="#d97706" stroke-width="2.5" stroke-opacity="0.6" fill="none" stroke-linecap="round"/>
                <path class="scroll-curve" data-speed="0.18" data-direction="-1"
                      d="M-150,620 Q250,520 550,670 T1050,570 T1550,720 T2050,620" 
                      stroke="#ea580c" stroke-width="2" stroke-opacity="0.5" fill="none" stroke-linecap="round"/>
                <path class="scroll-curve" data-speed="0.25" data-direction="1"
                      d="M50,800 Q450,700 850,850 T1450,750 T2050,900" 
                      stroke="#f59e0b" stroke-width="2.5" stroke-opacity="0.55" fill="none" stroke-linecap="round"/>
                      
                <!-- Dashed/dotted accent curves -->
                <path class="scroll-curve" data-speed="0.22" data-direction="-1"
                      d="M100,50 C400,150 700,0 1000,100 S1500,0 1800,100" 
                      stroke="#d97706" stroke-width="2.5" stroke-dasharray="25,15" stroke-opacity="0.65" fill="none"/>
                <path class="scroll-curve" data-speed="0.16" data-direction="1"
                      d="M-50,380 C250,280 550,430 850,330 S1350,430 1650,330 S1950,430 2250,330" 
                      stroke="#ea580c" stroke-width="2" stroke-dasharray="18,12" stroke-opacity="0.55" fill="none"/>
                <path class="scroll-curve" data-speed="0.28" data-direction="-1"
                      d="M200,700 Q600,600 1000,750 T1800,650" 
                      stroke="#f59e0b" stroke-width="2" stroke-dasharray="12,8" stroke-opacity="0.5" fill="none"/>
            </g>
            
            <!-- ===== REGULAR HEPTAGONS (7-sided) ===== -->
            <g class="heptagons-group">
                <polygon class="scroll-shape heptagon" data-speed="0.4" data-spin="1.2"
                         points="100,0 162,22 185,81 152,138 62,138 29,81 52,22"
                         transform="translate(150, 100)" 
                         stroke="#d97706" stroke-width="2.5" fill="none" opacity="0.5"/>
                <polygon class="scroll-shape heptagon" data-speed="0.35" data-spin="-0.8"
                         points="70,0 113,15 130,57 106,97 43,97 20,57 36,15"
                         transform="translate(1600, 200)" 
                         stroke="#ea580c" stroke-width="2" fill="none" opacity="0.45"/>
                <polygon class="scroll-shape heptagon" data-speed="0.5" data-spin="1.5"
                         points="80,0 129,18 148,65 121,111 49,111 23,65 42,18"
                         transform="translate(300, 500)" 
                         stroke="#f59e0b" stroke-width="2" stroke-dasharray="8,4" fill="none" opacity="0.4"/>
                <polygon class="scroll-shape heptagon" data-speed="0.3" data-spin="-1.0"
                         points="60,0 97,11 110,43 90,73 36,73 16,43 30,11"
                         transform="translate(1400, 650)" 
                         stroke="#d97706" stroke-width="2" fill="none" opacity="0.45"/>
            </g>
            
            <!-- ===== MOLECULE STRUCTURES ===== -->
            <g class="molecules-group">
                <!-- Molecule 1 - Large -->
                <g class="scroll-shape molecule" data-speed="0.45" data-spin="0.6" transform="translate(1700, 350)">
                    <circle cx="0" cy="0" r="12" fill="#d97706" opacity="0.7"/>
                    <circle cx="60" cy="-30" r="10" fill="#ea580c" opacity="0.6"/>
                    <circle cx="70" cy="40" r="8" fill="#f59e0b" opacity="0.65"/>
                    <circle cx="-50" cy="35" r="9" fill="#d97706" opacity="0.55"/>
                    <circle cx="-40" cy="-45" r="7" fill="#ea580c" opacity="0.6"/>
                    <line x1="0" y1="0" x2="60" y2="-30" stroke="#d97706" stroke-width="2" opacity="0.5"/>
                    <line x1="0" y1="0" x2="70" y2="40" stroke="#d97706" stroke-width="2" opacity="0.5"/>
                    <line x1="0" y1="0" x2="-50" y2="35" stroke="#d97706" stroke-width="2" opacity="0.5"/>
                    <line x1="0" y1="0" x2="-40" y2="-45" stroke="#d97706" stroke-width="2" opacity="0.5"/>
                    <line x1="60" y1="-30" x2="-40" y2="-45" stroke="#ea580c" stroke-width="1.5" opacity="0.4"/>
                </g>
                
                <!-- Molecule 2 - Medium -->
                <g class="scroll-shape molecule" data-speed="0.38" data-spin="-0.9" transform="translate(200, 700)">
                    <circle cx="0" cy="0" r="10" fill="#ea580c" opacity="0.65"/>
                    <circle cx="45" cy="-25" r="8" fill="#d97706" opacity="0.6"/>
                    <circle cx="50" cy="30" r="7" fill="#f59e0b" opacity="0.55"/>
                    <circle cx="-35" cy="25" r="8" fill="#d97706" opacity="0.6"/>
                    <circle cx="-45" cy="-20" r="6" fill="#ea580c" opacity="0.5"/>
                    <circle cx="0" cy="-55" r="7" fill="#f59e0b" opacity="0.55"/>
                    <line x1="0" y1="0" x2="45" y2="-25" stroke="#ea580c" stroke-width="1.8" opacity="0.5"/>
                    <line x1="0" y1="0" x2="50" y2="30" stroke="#ea580c" stroke-width="1.8" opacity="0.5"/>
                    <line x1="0" y1="0" x2="-35" y2="25" stroke="#ea580c" stroke-width="1.8" opacity="0.5"/>
                    <line x1="0" y1="0" x2="-45" y2="-20" stroke="#ea580c" stroke-width="1.8" opacity="0.5"/>
                    <line x1="0" y1="0" x2="0" y2="-55" stroke="#ea580c" stroke-width="1.8" opacity="0.5"/>
                    <line x1="45" y1="-25" x2="0" y2="-55" stroke="#d97706" stroke-width="1.5" opacity="0.4"/>
                </g>
                
                <!-- Molecule 3 - Benzene ring style -->
                <g class="scroll-shape molecule" data-speed="0.5" data-spin="0.75" transform="translate(900, 150)">
                    <polygon points="0,-40 35,-20 35,20 0,40 -35,20 -35,-20" 
                             stroke="#d97706" stroke-width="2.5" fill="none" opacity="0.6"/>
                    <circle cx="0" cy="-40" r="6" fill="#d97706" opacity="0.7"/>
                    <circle cx="35" cy="-20" r="6" fill="#ea580c" opacity="0.65"/>
                    <circle cx="35" cy="20" r="6" fill="#f59e0b" opacity="0.6"/>
                    <circle cx="0" cy="40" r="6" fill="#d97706" opacity="0.7"/>
                    <circle cx="-35" cy="20" r="6" fill="#ea580c" opacity="0.65"/>
                    <circle cx="-35" cy="-20" r="6" fill="#f59e0b" opacity="0.6"/>
                </g>
                
                <!-- Molecule 4 - Complex structure -->
                <g class="scroll-shape molecule" data-speed="0.42" data-spin="-0.5" transform="translate(1200, 850)">
                    <circle cx="0" cy="0" r="14" fill="#d97706" opacity="0.6"/>
                    <circle cx="70" cy="0" r="10" fill="#ea580c" opacity="0.55"/>
                    <circle cx="35" cy="-60" r="8" fill="#f59e0b" opacity="0.5"/>
                    <circle cx="35" cy="60" r="8" fill="#d97706" opacity="0.55"/>
                    <circle cx="-50" cy="-35" r="9" fill="#ea580c" opacity="0.5"/>
                    <circle cx="-50" cy="35" r="9" fill="#f59e0b" opacity="0.5"/>
                    <line x1="0" y1="0" x2="70" y2="0" stroke="#d97706" stroke-width="2" opacity="0.5"/>
                    <line x1="0" y1="0" x2="35" y2="-60" stroke="#d97706" stroke-width="2" opacity="0.5"/>
                    <line x1="0" y1="0" x2="35" y2="60" stroke="#d97706" stroke-width="2" opacity="0.5"/>
                    <line x1="0" y1="0" x2="-50" y2="-35" stroke="#d97706" stroke-width="2" opacity="0.5"/>
                    <line x1="0" y1="0" x2="-50" y2="35" stroke="#d97706" stroke-width="2" opacity="0.5"/>
                </g>
            </g>
            
            <!-- ===== OTHER POLYGONS ===== -->
            <g class="polygons-group">
                <!-- Pentagon -->
                <polygon class="scroll-shape" data-speed="0.35" data-spin="0.9"
                         points="50,0 97,35 80,90 20,90 3,35"
                         transform="translate(500, 300)" 
                         stroke="#ea580c" stroke-width="2" fill="none" opacity="0.45"/>
                         
                <!-- Octagon -->
                <polygon class="scroll-shape" data-speed="0.4" data-spin="-0.7"
                         points="30,0 70,0 100,30 100,70 70,100 30,100 0,70 0,30"
                         transform="translate(1100, 450)" 
                         stroke="#d97706" stroke-width="2.5" fill="none" opacity="0.5"/>
                         
                <!-- Hexagon -->
                <polygon class="scroll-shape" data-speed="0.32" data-spin="1.1"
                         points="50,0 93,25 93,75 50,100 7,75 7,25"
                         transform="translate(700, 750)" 
                         stroke="#f59e0b" stroke-width="2" fill="none" opacity="0.45"/>
                         
                <!-- Triangle -->
                <polygon class="scroll-shape" data-speed="0.48" data-spin="-1.3"
                         points="40,0 80,70 0,70"
                         transform="translate(1500, 550)" 
                         stroke="#d97706" stroke-width="2.5" fill="none" opacity="0.5"/>
            </g>
            
            <!-- ===== CIRCLES WITH ORBITS ===== -->
            <g class="orbits-group">
                <g class="scroll-shape orbit-system" data-speed="0.38" data-spin="0.4" transform="translate(400, 150)">
                    <circle cx="0" cy="0" r="8" fill="#d97706" opacity="0.7"/>
                    <ellipse cx="0" cy="0" rx="50" ry="25" stroke="#d97706" stroke-width="1.5" fill="none" opacity="0.4" transform="rotate(-20)"/>
                    <ellipse cx="0" cy="0" rx="35" ry="18" stroke="#ea580c" stroke-width="1.5" fill="none" opacity="0.35" transform="rotate(30)"/>
                    <circle cx="48" cy="-8" r="4" fill="#ea580c" opacity="0.6"/>
                    <circle cx="-30" cy="15" r="3" fill="#f59e0b" opacity="0.55"/>
                </g>
                
                <g class="scroll-shape orbit-system" data-speed="0.45" data-spin="-0.55" transform="translate(1300, 300)">
                    <circle cx="0" cy="0" r="10" fill="#ea580c" opacity="0.65"/>
                    <ellipse cx="0" cy="0" rx="60" ry="30" stroke="#ea580c" stroke-width="1.5" fill="none" opacity="0.4" transform="rotate(15)"/>
                    <ellipse cx="0" cy="0" rx="40" ry="20" stroke="#d97706" stroke-width="1.5" fill="none" opacity="0.35" transform="rotate(-25)"/>
                    <circle cx="55" cy="18" r="5" fill="#d97706" opacity="0.6"/>
                    <circle cx="-38" cy="-12" r="4" fill="#f59e0b" opacity="0.55"/>
                </g>
            </g>
            
            <!-- ===== DECORATIVE ELEMENTS ===== -->
            <g class="decor-group">
                <!-- Plus signs -->
                <g class="scroll-shape" data-speed="0.3" data-spin="2.0" transform="translate(600, 550)">
                    <line x1="-20" y1="0" x2="20" y2="0" stroke="#d97706" stroke-width="3" opacity="0.5"/>
                    <line x1="0" y1="-20" x2="0" y2="20" stroke="#d97706" stroke-width="3" opacity="0.5"/>
                </g>
                <g class="scroll-shape" data-speed="0.35" data-spin="-1.8" transform="translate(1000, 250)">
                    <line x1="-15" y1="0" x2="15" y2="0" stroke="#ea580c" stroke-width="2.5" opacity="0.45"/>
                    <line x1="0" y1="-15" x2="0" y2="15" stroke="#ea580c" stroke-width="2.5" opacity="0.45"/>
                </g>
                <g class="scroll-shape" data-speed="0.42" data-spin="1.5" transform="translate(1650, 700)">
                    <line x1="-18" y1="0" x2="18" y2="0" stroke="#f59e0b" stroke-width="2.5" opacity="0.5"/>
                    <line x1="0" y1="-18" x2="0" y2="18" stroke="#f59e0b" stroke-width="2.5" opacity="0.5"/>
                </g>
                
                <!-- Dot patterns -->
                <g class="scroll-shape" data-speed="0.25" data-spin="0.3" transform="translate(850, 600)">
                    <circle cx="0" cy="0" r="4" fill="#d97706" opacity="0.5"/>
                    <circle cx="20" cy="0" r="4" fill="#d97706" opacity="0.45"/>
                    <circle cx="40" cy="0" r="4" fill="#d97706" opacity="0.4"/>
                    <circle cx="10" cy="17" r="4" fill="#d97706" opacity="0.45"/>
                    <circle cx="30" cy="17" r="4" fill="#d97706" opacity="0.4"/>
                    <circle cx="20" cy="34" r="4" fill="#d97706" opacity="0.35"/>
                </g>
                
                <!-- Concentric circles -->
                <g class="scroll-shape" data-speed="0.28" data-spin="0.2" transform="translate(250, 450)">
                    <circle cx="0" cy="0" r="15" stroke="#d97706" stroke-width="2" fill="none" opacity="0.5"/>
                    <circle cx="0" cy="0" r="30" stroke="#d97706" stroke-width="1.5" fill="none" opacity="0.4"/>
                    <circle cx="0" cy="0" r="45" stroke="#d97706" stroke-width="1" fill="none" opacity="0.3"/>
                </g>
                <g class="scroll-shape" data-speed="0.32" data-spin="-0.25" transform="translate(1450, 150)">
                    <circle cx="0" cy="0" r="12" stroke="#ea580c" stroke-width="2" fill="none" opacity="0.5"/>
                    <circle cx="0" cy="0" r="25" stroke="#ea580c" stroke-width="1.5" fill="none" opacity="0.4"/>
                    <circle cx="0" cy="0" r="38" stroke="#ea580c" stroke-width="1" fill="none" opacity="0.3"/>
                </g>
            </g>
        </svg>

        <!-- Legacy geometric layers (triangles, squares, diamonds, etc.) -->
        <div class="geo-shape geo-circle scroll-geo" data-speed="0.3" data-spin="0.2"
             style="width: 280px; height: 280px; top: -80px; right: 5%; border: 3px solid #d97706; opacity: 0.4;"></div>
        <div class="geo-shape geo-circle scroll-geo" data-speed="0.5" data-spin="0.25"
             style="width: 180px; height: 180px; top: 25%; left: -60px; border: 2px solid #ea580c; opacity: 0.35;"></div>
        <div class="geo-shape geo-circle scroll-geo" data-speed="0.2" data-spin="0.15"
             style="width: 120px; height: 120px; top: 55%; right: 12%; border: 2px dashed #f59e0b; opacity: 0.4;"></div>
        <div class="geo-shape geo-circle scroll-geo" data-speed="0.4" data-spin="0.18"
             style="width: 200px; height: 200px; bottom: 15%; left: 8%; border: 2.5px solid #d97706; opacity: 0.3;"></div>

        <!-- Triangles -->
        <div class="scroll-geo geo-triangle-shape" data-speed="0.35" data-spin="0.5" style="top: 12%; left: 15%;"></div>
        <div class="scroll-geo geo-triangle-shape geo-triangle-shape--inverted" data-speed="0.45" data-spin="0.4" style="bottom: 25%; right: 18%;"></div>
        <div class="scroll-geo geo-triangle-shape geo-triangle-shape--small" data-speed="0.25" data-spin="0.6" style="top: 45%; right: 30%;"></div>

        <!-- Squares/Diamonds -->
        <div class="geo-shape scroll-geo geo-square" data-speed="0.35" data-spin="0.4" style="width: 70px; height: 70px; top: 32%; left: 10%;"></div>
        <div class="geo-shape scroll-geo geo-square geo-square--small" data-speed="0.25" data-spin="0.3" style="width: 50px; height: 50px; top: 20%; right: 28%;"></div>
        <div class="geo-shape scroll-geo geo-diamond" data-speed="0.4" data-spin="0.5" style="width: 70px; height: 70px; top: 35%; left: 6%;"></div>
        <div class="geo-shape scroll-geo geo-diamond" data-speed="0.3" data-spin="0.45" style="width: 50px; height: 50px; top: 18%; right: 22%;"></div>
        <div class="geo-shape scroll-geo geo-diamond geo-diamond--outline" data-speed="0.5" data-spin="0.6" style="width: 90px; height: 90px; bottom: 30%; right: 8%;"></div>

        <!-- Hexagons -->
        <div class="scroll-geo geo-hexagon-shape" data-speed="0.35" data-spin="0.4" style="top: 65%; left: 20%;"></div>
        <div class="scroll-geo geo-hexagon-shape geo-hexagon-shape--small" data-speed="0.25" data-spin="0.35" style="top: 8%; left: 40%;"></div>

        <!-- Plus signs -->
        <div class="scroll-geo geo-plus" data-speed="0.3" data-spin="0.6" style="top: 22%; left: 28%;"></div>
        <div class="scroll-geo geo-plus geo-plus--small" data-speed="0.4" data-spin="0.7" style="top: 48%; right: 5%;"></div>
        <div class="scroll-geo geo-plus" data-speed="0.35" data-spin="0.5" style="bottom: 18%; left: 35%;"></div>

        <!-- Dot clusters -->
        <div class="scroll-geo dot-cluster" data-speed="0.2" data-spin="0.2" style="top: 15%; right: 35%;"></div>
        <div class="scroll-geo dot-cluster" data-speed="0.3" data-spin="0.25" style="bottom: 35%; left: 45%;"></div>

        <!-- Concentric expanding rings -->
        <div class="scroll-geo concentric-set" data-speed="0.25" data-spin="0.2" style="top: 40%; left: 10%;">
            <div class="c-ring c-ring--1"></div>
            <div class="c-ring c-ring--2"></div>
            <div class="c-ring c-ring--3"></div>
        </div>
        <div class="scroll-geo concentric-set" data-speed="0.35" data-spin="0.25" style="bottom: 20%; right: 25%;">
            <div class="c-ring c-ring--1"></div>
            <div class="c-ring c-ring--2"></div>
            <div class="c-ring c-ring--3"></div>
        </div>
    </div>
    """)


def initialize_session_state():
    """Initialize session state variables."""
    if "doc_id" not in st.session_state:
        st.session_state.doc_id = None
    if "processing" not in st.session_state:
        st.session_state.processing = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "document" not in st.session_state:
        st.session_state.document = None


def get_confidence_class(confidence: float) -> str:
    """Get CSS class based on confidence level."""
    if confidence >= 0.9:
        return "confidence-high"
    elif confidence >= 0.7:
        return "confidence-medium"
    else:
        return "confidence-low"


def format_confidence(confidence: float) -> str:
    """Format confidence as percentage with color."""
    css_class = get_confidence_class(confidence)
    return f'<span class="{css_class}">{confidence:.0%}</span>'


def process_document(file_content: bytes, filename: str) -> str:
    """Process uploaded document."""
    store = get_document_store()
    loader = get_document_loader()
    ocr_engine = get_ocr_engine()
    text_processor = get_text_processor()
    entity_extractor = get_entity_extractor()
    vector_store = get_document_vector_store()
    summarizer = get_summarizer()

    # Get file info
    ext = "." + filename.lower().split(".")[-1] if "." in filename else ""

    # Create document
    doc_id = store.create_document(
        filename=filename,
        file_type=ext,
        file_size_bytes=len(file_content)
    )

    progress_bar = st.progress(0, text="Loading document...")

    try:
        # Step 1: Load document
        store.set_status(doc_id, DocumentStatus.PROCESSING)
        load_result = loader.load(file_content, filename)

        if not load_result:
            store.set_error(doc_id, "Failed to load document")
            return doc_id

        progress_bar.progress(20, text="Extracting text...")

        # Step 2: Extract text
        from app.models import PageContent
        pages = []
        all_text = []
        image_idx = 0

        for page in load_result.pages:
            page_text = page.text or ""
            ocr_confidence = None
            is_scanned = page.is_scanned

            if is_scanned and image_idx < len(load_result.images):
                ocr_result = ocr_engine.process_image(load_result.images[image_idx])
                if ocr_result and ocr_result.text:
                    page_text = ocr_result.text
                    ocr_confidence = ocr_result.confidence
                image_idx += 1

            pages.append(PageContent(
                page_number=page.page_number,
                text=page_text,
                is_scanned=is_scanned,
                ocr_confidence=ocr_confidence
            ))
            all_text.append(page_text)

        progress_bar.progress(40, text="Processing text...")

        # Update document
        doc = store.get_document(doc_id)
        doc.pages = pages
        doc.raw_text = "\n\n".join(all_text)
        doc.metadata.page_count = load_result.page_count
        doc.metadata.is_scanned = load_result.is_scanned

        # Step 3: Process text
        processed = text_processor.process(doc.raw_text)
        doc.chunks = processed.chunks

        progress_bar.progress(60, text="Extracting entities...")

        # Step 4: Extract entities
        doc.entities = entity_extractor.extract(doc.raw_text)

        progress_bar.progress(75, text="Indexing document...")

        # Step 5: Index in vector store
        if doc.chunks:
            vector_store.index_document(doc_id, doc.chunks)

        progress_bar.progress(90, text="Generating summary...")

        # Step 6: Generate summary
        word_count = len(doc.raw_text.split())
        doc.summary = summarizer.summarize(
            doc.raw_text,
            word_count=word_count,
            page_count=doc.metadata.page_count
        )

        # Complete
        store.update_document(doc_id, doc)
        store.set_status(doc_id, DocumentStatus.COMPLETED)
        progress_bar.progress(100, text="Complete!")

        return doc_id

    except Exception as e:
        store.set_error(doc_id, str(e))
        st.error(f"Processing failed: {e}")
        return doc_id


def render_upload_tab():
    """Render the upload tab."""
    # Section header
    render_html(f"""
    <div class="section__head motion-reveal motion-reveal--delay-1">
        <div class="section__icon">
            {get_icon('upload', 18)}
        </div>
        <div>
            <h2 class="section__title">Upload Document</h2>
            <p class="section__desc">Upload a PDF or image file to analyze</p>
        </div>
    </div>
    """)

    uploaded_file = st.file_uploader(
        "Choose a document",
        type=["pdf", "png", "jpg", "jpeg", "tiff"],
        help="Supported formats: PDF, PNG, JPG, JPEG, TIFF (max 25MB)",
        label_visibility="collapsed"
    )

    if uploaded_file is not None:
        # Show file info in styled cards
        render_html("""
        <div class="motion-reveal motion-reveal--delay-2" style="margin: 1.5rem 0 1rem 0;">
            <p style="font-size: 0.875rem; font-weight: 600; color: #374151; margin-bottom: 0.75rem;">File Information</p>
        </div>
        """)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name[:20] + "..." if len(uploaded_file.name) > 20 else uploaded_file.name)
        with col2:
            st.metric("Size", f"{uploaded_file.size / 1024:.1f} KB")
        with col3:
            file_type = uploaded_file.type.split('/')[-1].upper() if uploaded_file.type else "Unknown"
            st.metric("Type", file_type)

        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        
        if st.button("Process Document", type="primary", use_container_width=True):
            with st.spinner("Processing document..."):
                file_content = uploaded_file.read()
                doc_id = process_document(file_content, uploaded_file.name)
                st.session_state.doc_id = doc_id
                st.session_state.document = get_document_store().get_document(doc_id)
                st.session_state.chat_history = []
                st.success(f"Document processed successfully!")
                st.rerun()
    else:
        # Empty state
        render_html(f"""
        <div class="upload-zone motion-reveal motion-reveal--delay-2 motion-hover motion-hover--soft" style="margin-top: 1rem;">
            <div class="upload-zone__icon">
                {get_icon('upload', 28)}
            </div>
            <p class="upload-zone__title">Drag and drop your document</p>
            <p class="upload-zone__desc">or click above to browse files</p>
        </div>
        """)


def render_summary_tab():
    """Render the summary tab."""
    # Section header
    render_html(f"""
    <div class="section__head motion-reveal motion-reveal--delay-1">
        <div class="section__icon">
            {get_icon('file-text', 18)}
        </div>
        <div>
            <h2 class="section__title">Document Summary</h2>
            <p class="section__desc">AI-generated overview and key insights</p>
        </div>
    </div>
    """)

    if not st.session_state.document:
        st.info("Please upload a document first.")
        return

    doc = st.session_state.document

    if doc.status != DocumentStatus.COMPLETED:
        st.warning(f"Document status: {doc.status.value}")
        return

    # Document metadata in styled cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pages", doc.metadata.page_count)
    with col2:
        st.metric("Words", doc.summary.word_count if doc.summary else 0)
    with col3:
        st.metric("Scanned", "Yes" if doc.metadata.is_scanned else "No")
    with col4:
        doc_type = doc.summary.document_type.value if doc.summary else "unknown"
        st.metric("Type", doc_type.title())

    st.divider()

    if doc.summary:
        # Executive Summary in a card
        render_html(f"""
        <div class="card motion-reveal motion-reveal--delay-2 motion-hover" style="margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                <div class="section__icon" style="width: 32px; height: 32px;">
                    {get_icon('layers', 16)}
                </div>
                <h3 style="margin: 0; font-size: 1rem; font-weight: 600; color: #111827;">Executive Summary</h3>
            </div>
            <p style="margin: 0; font-size: 0.9375rem; color: #374151; line-height: 1.7;">
                {doc.summary.executive_summary}
            </p>
        </div>
        """)

        # Key Points
        render_html(f"""
        <div class="motion-reveal motion-reveal--delay-3" style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
            <div class="section__icon" style="width: 32px; height: 32px;">
                {get_icon('list', 16)}
            </div>
            <h3 style="margin: 0; font-size: 1rem; font-weight: 600; color: #111827;">Key Points</h3>
        </div>
        """)
        
        for i, point in enumerate(doc.summary.key_points, 1):
            st.markdown(f'<div class="key-point motion-reveal motion-reveal--delay-4"><strong>{i}.</strong> {point}</div>',
                       unsafe_allow_html=True)
    else:
        st.warning("Summary not available.")


def render_entities_tab():
    """Render the entities tab."""
    # Section header
    render_html(f"""
    <div class="section__head motion-reveal motion-reveal--delay-1">
        <div class="section__icon">
            {get_icon('search', 18)}
        </div>
        <div>
            <h2 class="section__title">Extracted Entities</h2>
            <p class="section__desc">Automatically detected data points from your document</p>
        </div>
    </div>
    """)

    if not st.session_state.document:
        st.info("Please upload a document first.")
        return

    doc = st.session_state.document

    if doc.status != DocumentStatus.COMPLETED:
        st.warning(f"Document status: {doc.status.value}")
        return

    entities = doc.entities

    # Entity type filter
    entity_types = ["All", "Dates", "Amounts", "Persons", "Organizations",
                   "Emails", "Phones", "Invoice Numbers", "GSTINs", "PANs"]
    selected_type = st.selectbox("Filter by type", entity_types, label_visibility="collapsed")

    # Stats in styled metric cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Entities", entities.total_count)
    with col2:
        high_conf = sum(1 for e in entities.to_flat_list() if e.confidence >= 0.9)
        st.metric("High Confidence", high_conf)
    with col3:
        unique_types = len([t for t in [entities.dates, entities.amounts, entities.persons,
                                        entities.organizations, entities.emails, entities.phones,
                                        entities.invoice_numbers, entities.gstins, entities.pans]
                          if t])
        st.metric("Entity Types", unique_types)

    st.divider()

    # Render entities by type
    def render_entity_section(title: str, items: list, show_extra: str = None):
        if not items:
            return
        if selected_type != "All" and selected_type != title:
            return

        render_html(f"""
        <div class="motion-reveal motion-reveal--delay-2" style="display: flex; align-items: center; gap: 0.5rem; margin: 1.5rem 0 0.75rem 0;">
            <span class="badge badge--brand">{len(items)}</span>
            <h3 style="margin: 0; font-size: 1rem; font-weight: 600; color: #111827;">{title}</h3>
        </div>
        """)
        
        for item in items:
            conf_html = format_confidence(item.confidence)
            extra_info = ""
            if show_extra == "parsed_date" and hasattr(item, 'parsed_date') and item.parsed_date:
                extra_info = f' <span class="badge badge--neutral">Parsed: {item.parsed_date.strftime("%Y-%m-%d")}</span>'
            elif show_extra == "amount" and hasattr(item, 'numeric_value'):
                numeric_value = getattr(item, 'numeric_value', None)
                currency = getattr(item, 'currency', '') or ''
                if numeric_value is not None:
                    formatted_value = f"{numeric_value:,.2f}"
                    label = f"{currency} {formatted_value}".strip()
                    extra_info = f' <span class="badge badge--success">{label}</span>'

            page_info = f' <span class="badge badge--neutral">Page {item.page_number}</span>' if item.page_number else ""

            st.markdown(
                f'<div class="entity-card motion-reveal motion-hover motion-hover--soft">'
                f'<div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.5rem;">'
                f'<strong style="color: #111827;">{item.value}</strong>'
                f'<span style="font-size: 0.8rem;">Confidence: {conf_html}</span>'
                f'</div>'
                f'<div style="margin-top: 0.5rem; display: flex; gap: 0.5rem; flex-wrap: wrap;">{extra_info}{page_info}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    render_entity_section("Dates", entities.dates, "parsed_date")
    render_entity_section("Amounts", entities.amounts, "amount")
    render_entity_section("Persons", entities.persons)
    render_entity_section("Organizations", entities.organizations)
    render_entity_section("Emails", entities.emails)
    render_entity_section("Phones", entities.phones)
    render_entity_section("Invoice Numbers", entities.invoice_numbers)
    render_entity_section("GSTINs", entities.gstins)
    render_entity_section("PANs", entities.pans)


def render_qa_tab():
    """Render the Q&A tab."""
    # Section header
    render_html(f"""
    <div class="section__head motion-reveal motion-reveal--delay-1">
        <div class="section__icon">
            {get_icon('message-circle', 18)}
        </div>
        <div>
            <h2 class="section__title">Ask Questions</h2>
            <p class="section__desc">Chat with your document using AI</p>
        </div>
    </div>
    """)

    if not st.session_state.document:
        st.info("Please upload a document first.")
        return

    doc = st.session_state.document

    if doc.status != DocumentStatus.COMPLETED:
        st.warning(f"Document status: {doc.status.value}")
        return

    # Chat history display
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-message user-message motion-reveal motion-reveal--delay-1">'
                f'<strong>You:</strong> {msg["content"]}'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            sources_html = ""
            if msg.get("sources"):
                sources_html = "<div class='source-citation'><strong>Sources:</strong> "
                for src in msg["sources"]:
                    if src.page:
                        sources_html += f"Page {src.page}, "
                    if src.quote:
                        sources_html += f'"{src.quote[:50]}...", '
                sources_html = sources_html.rstrip(", ") + "</div>"

            st.markdown(
                f'<div class="chat-message assistant-message motion-reveal motion-reveal--delay-1">'
                f'<strong>Assistant:</strong> {msg["content"]}'
                f'{sources_html}'
                f'</div>',
                unsafe_allow_html=True
            )

    # Suggested questions
    qa_engine = get_qa_engine()
    if not st.session_state.chat_history:
        render_html(f"""
        <div class="card motion-reveal motion-reveal--delay-2 motion-hover motion-hover--soft" style="margin: 1rem 0; padding: 1.25rem; background: linear-gradient(135deg, #fffbeb 0%, #fff7ed 100%);">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
                <div class="section__icon" style="width: 28px; height: 28px; background: linear-gradient(135deg, #d97706, #f59e0b);">
                    {get_icon('sparkles', 14)}
                </div>
                <span style="font-weight: 600; color: #1a1714;">Suggested Questions</span>
            </div>
        </div>
        """)
        
        questions = qa_engine.generate_suggested_questions(st.session_state.doc_id)
        cols = st.columns(min(len(questions), 3))
        for i, q in enumerate(questions[:3]):
            with cols[i]:
                if st.button(q, key=f"suggested_{i}", use_container_width=True):
                    st.session_state.pending_question = q
                    st.rerun()

    # Question input
    question = st.chat_input("Ask a question about the document...")

    # Handle pending question from suggested
    if hasattr(st.session_state, 'pending_question') and st.session_state.pending_question:
        question = st.session_state.pending_question
        st.session_state.pending_question = None

    if question:
        # Add user message
        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })

        # Get answer
        with st.spinner("Thinking..."):
            from app.models import QAMessage
            history = [
                QAMessage(role=msg["role"], content=msg["content"])
                for msg in st.session_state.chat_history[:-1]  # Exclude current question
            ]
            response = qa_engine.answer(
                doc_id=st.session_state.doc_id,
                question=question,
                conversation_history=history
            )

        # Add assistant response
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response.answer,
            "sources": response.sources,
            "confidence": response.confidence
        })

        st.rerun()


def render_export_tab():
    """Render the export tab."""
    # Section header
    render_html(f"""
    <div class="section__head motion-reveal motion-reveal--delay-1">
        <div class="section__icon">
            {get_icon('download', 18)}
        </div>
        <div>
            <h2 class="section__title">Export Data</h2>
            <p class="section__desc">Download your processed document data</p>
        </div>
    </div>
    """)

    if not st.session_state.document:
        st.info("Please upload a document first.")
        return

    doc = st.session_state.document

    if doc.status != DocumentStatus.COMPLETED:
        st.warning(f"Document status: {doc.status.value}")
        return

    exporter = get_exporter()

    # Export options in a card
    render_html("""
    <div class="card motion-reveal motion-reveal--delay-2 motion-hover motion-hover--soft" style="margin-bottom: 1.5rem; padding: 1.25rem;">
        <h3 style="margin: 0 0 1rem 0; font-size: 0.9375rem; font-weight: 600; color: #111827;">Export Options</h3>
    </div>
    """)

    col1, col2 = st.columns(2)
    with col1:
        include_summary = st.checkbox("Include Summary", value=True)
        include_entities = st.checkbox("Include Entities", value=True)
    with col2:
        include_raw_text = st.checkbox("Include Raw Text", value=False)

    st.divider()

    # Export format cards
    render_html("""
    <p style="font-size: 0.875rem; font-weight: 600; color: #374151; margin-bottom: 1rem;">Choose Export Format</p>
    """)

    col1, col2, col3 = st.columns(3)

    with col1:
        render_html("""
        <div class="dl-card motion-reveal motion-reveal--delay-2 motion-hover">
            <div class="dl-card__icon dl-card__icon--json">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><path d="M12 12v6"/><path d="M9 15c0 1.5 1 2 2 2h2c1 0 2-.5 2-2s-1-2-2-2h-2c-1 0-2-.5-2-2s1-2 2-2h2c1 0 2 .5 2 2"/></svg>
            </div>
            <div class="dl-card__body">
                <p class="dl-card__name">JSON Export</p>
                <p class="dl-card__meta">Structured data format</p>
            </div>
        </div>
        """)
        json_data = exporter.export(
            doc, ExportFormat.JSON,
            include_summary, include_entities, include_raw_text
        )
        st.download_button(
            "Download JSON",
            json_data,
            f"{st.session_state.doc_id}_export.json",
            "application/json",
            use_container_width=True
        )

    with col2:
        render_html("""
        <div class="dl-card motion-reveal motion-reveal--delay-2 motion-hover">
            <div class="dl-card__icon dl-card__icon--csv">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><path d="M8 13h2"/><path d="M14 13h2"/><path d="M8 17h2"/><path d="M14 17h2"/></svg>
            </div>
            <div class="dl-card__body">
                <p class="dl-card__name">CSV Export</p>
                <p class="dl-card__meta">Flattened entities table</p>
            </div>
        </div>
        """)
        csv_data = exporter.export(doc, ExportFormat.CSV)
        st.download_button(
            "Download CSV",
            csv_data,
            f"{st.session_state.doc_id}_entities.csv",
            "text/csv",
            use_container_width=True
        )

    with col3:
        render_html("""
        <div class="dl-card motion-reveal motion-reveal--delay-2 motion-hover">
            <div class="dl-card__icon dl-card__icon--excel">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><path d="M8 13h8"/><path d="M8 17h8"/><path d="M8 9h8"/></svg>
            </div>
            <div class="dl-card__body">
                <p class="dl-card__name">Excel Export</p>
                <p class="dl-card__meta">Formatted workbook</p>
            </div>
        </div>
        """)
        excel_data = exporter.export(
            doc, ExportFormat.EXCEL,
            include_summary, include_entities, include_raw_text
        )
        st.download_button(
            "Download Excel",
            excel_data,
            f"{st.session_state.doc_id}_export.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    # Preview section
    st.divider()
    
    render_html(f"""
    <div class="motion-reveal motion-reveal--delay-2" style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
        <div class="section__icon" style="width: 28px; height: 28px;">
            {get_icon('layers', 14)}
        </div>
        <h3 style="margin: 0; font-size: 0.9375rem; font-weight: 600; color: #111827;">Preview</h3>
    </div>
    """)

    preview_format = st.selectbox("Preview format", ["JSON", "CSV"], label_visibility="collapsed")

    if preview_format == "JSON":
        st.json(json_data[:5000] + "..." if len(json_data) > 5000 else json_data)
    else:
        # Parse CSV and show as table
        csv_lines = csv_data.strip().split("\n")
        if len(csv_lines) > 1:
            import csv
            reader = csv.reader(io.StringIO(csv_data))
            rows = list(reader)
            if rows:
                df = pd.DataFrame(rows[1:], columns=rows[0])
                st.dataframe(df, use_container_width=True)


def render_sidebar():
    """Render sidebar with document info."""
    # Sidebar header with icon and branding
    render_html(f"""
    <div style="text-align: center; padding: 1rem 0 0.5rem 0;">
        <div class="app-header__icon" style="margin: 0 auto 0.75rem auto; width: 48px; height: 48px;">
            {get_icon('document', 22)}
        </div>
        <h2 class="main-header" style="font-size: 1.5rem !important; margin-bottom: 0.25rem !important;">Document Intelligence</h2>
        <p class="sub-header" style="font-size: 0.875rem !important;">AI-powered document analysis</p>
    </div>
    """)

    if st.session_state.document:
        doc = st.session_state.document
        st.sidebar.divider()
        
        # Document info card
        render_html(f"""
        <div class="card" style="padding: 1rem; margin-bottom: 0.75rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
                <div class="section__icon" style="width: 28px; height: 28px;">
                    {get_icon('file-text', 14)}
                </div>
                <span style="font-weight: 600; color: #1a1714;">Current Document</span>
            </div>
            <div style="font-size: 0.875rem; color: #5c554a;">
                <p style="margin: 0.25rem 0;"><strong>File:</strong> {doc.metadata.filename}</p>
                <p style="margin: 0.25rem 0;"><strong>Status:</strong> 
                    <span class="badge badge--{'success' if doc.status == DocumentStatus.COMPLETED else 'warning'}">{doc.status.value}</span>
                </p>
                <p style="margin: 0.25rem 0;"><strong>Pages:</strong> {doc.metadata.page_count}</p>
            </div>
        </div>
        """)

        if st.sidebar.button("Clear Document", use_container_width=True, type="secondary"):
            # Clean up
            if st.session_state.doc_id:
                store = get_document_store()
                vector_store = get_document_vector_store()
                try:
                    vector_store.delete_store(st.session_state.doc_id)
                except:
                    pass
                store.delete_document(st.session_state.doc_id)

            st.session_state.doc_id = None
            st.session_state.document = None
            st.session_state.chat_history = []
            st.rerun()

    st.sidebar.divider()
    
    # Features card with orange gradient
    render_html(f"""
    <div class="card" style="padding: 1rem; background: linear-gradient(135deg, #fffbeb 0%, #fff7ed 100%);">
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
            <div class="section__icon" style="width: 28px; height: 28px; background: linear-gradient(135deg, #d97706, #ea580c);">
                {get_icon('sparkles', 14)}
            </div>
            <span style="font-weight: 600; color: #1a1714;">Features</span>
        </div>
        <ul style="margin: 0; padding-left: 1.25rem; font-size: 0.8rem; color: #5c554a; line-height: 1.8;">
            <li>PDF and image processing</li>
            <li>OCR for scanned documents</li>
            <li>Entity extraction</li>
            <li>AI-powered summarization</li>
            <li>Q&A with citations</li>
            <li>Export to JSON/CSV/Excel</li>
        </ul>
    </div>
    """)


def render_app_header():
    """Render the main app header."""
    render_html(f"""
    <div class="app-header">
        <div class="app-header__icon motion-reveal motion-reveal--delay-1">
            {get_icon('document', 28)}
        </div>
        <h1 class="app-header__title motion-reveal motion-reveal--delay-2">Document Intelligence</h1>
        <p class="app-header__subtitle motion-reveal motion-reveal--delay-3">
            Upload documents to extract insights, entities, and answers using AI
        </p>
        <div class="app-header__tag motion-reveal motion-reveal--delay-4 motion-hover motion-hover--soft">
            {get_icon('sparkles', 14)}
            <span>AI-Powered Analysis</span>
        </div>
    </div>
    """)


def render_footer():
    """Render the app footer."""
    render_html(f"""
    <div class="app-footer motion-fade">
        <div class="app-footer__brand">
            {get_icon('zap', 14)}
            <span>Document Intelligence</span>
        </div>
        <p style="margin: 0;">Powered by AI for intelligent document processing</p>
    </div>
    """)


def render_document_info_bar():
    """Render a compact document info bar at the top when document is loaded."""
    if st.session_state.document:
        doc = st.session_state.document
        render_html(f"""
        <div class="doc-info-bar motion-reveal motion-reveal--delay-1 motion-hover motion-hover--soft">
            <div class="doc-info-bar__left">
                <div class="doc-info-bar__icon">
                    {get_icon('file-text', 16)}
                </div>
                <div class="doc-info-bar__details">
                    <span class="doc-info-bar__filename">{doc.metadata.filename}</span>
                    <span class="doc-info-bar__meta">{doc.metadata.page_count} pages</span>
                </div>
            </div>
            <div class="doc-info-bar__right">
                <span class="badge badge--{'success' if doc.status == DocumentStatus.COMPLETED else 'warning'}">{doc.status.value}</span>
            </div>
        </div>
        """)
        
        # Clear document button
        col1, col2, col3 = st.columns([3, 1, 3])
        with col2:
            if st.button("Clear", use_container_width=True, type="secondary"):
                if st.session_state.doc_id:
                    store = get_document_store()
                    vector_store = get_document_vector_store()
                    try:
                        vector_store.delete_store(st.session_state.doc_id)
                    except:
                        pass
                    store.delete_document(st.session_state.doc_id)
                st.session_state.doc_id = None
                st.session_state.document = None
                st.session_state.chat_history = []
                st.rerun()


def main():
    """Main application entry point."""
    initialize_session_state()

    # Render animated geometric background
    render_animated_background()

    # Render main app header (only on upload page)
    if not (st.session_state.document and st.session_state.document.status == DocumentStatus.COMPLETED):
        render_app_header()
    else:
        # Show compact document info bar
        render_document_info_bar()

    # Main content with tabs
    if st.session_state.document and st.session_state.document.status == DocumentStatus.COMPLETED:
        tabs = st.tabs(["Summary", "Entities", "Q&A", "Export", "Upload New"])

        with tabs[0]:
            render_summary_tab()
        with tabs[1]:
            render_entities_tab()
        with tabs[2]:
            render_qa_tab()
        with tabs[3]:
            render_export_tab()
        with tabs[4]:
            render_upload_tab()
    else:
        # Show upload tab only
        render_upload_tab()
    
    # Render footer
    render_footer()


if __name__ == "__main__":
    main()
