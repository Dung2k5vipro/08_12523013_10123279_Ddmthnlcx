# -*- coding: utf-8 -*-
"""
Script to generate the standardized academic report docs/baocao.docx
based on docs/mau_bao_cao.docx and requirements:
1. Standard Academic Layout:
   - Outer Cover (Bìa chính) & Inner Cover (Bìa phụ)
   - Nhận xét của giảng viên hướng dẫn
   - Lời cam đoan
   - Lời cảm ơn
   - MỤC LỤC (Clickable + Dot Leaders + Editable/PAGEREF Page Numbers)
   - DANH MỤC BẢNG (Clickable + Dot Leaders + Editable/PAGEREF Page Numbers)
   - DANH MỤC HÌNH ÁNH (Clickable + Dot Leaders + Editable/PAGEREF Page Numbers)
   - DANH MỤC TỪ VIẾT TẮT (with Table of Abbreviations)
   - Main content: Chương 1 to 5 + Phần sau báo cáo (Phân công, Tài liệu tham khảo, Phụ lục)
2. Added Figures for Chapter 1 and Chapter 2:
   - Chapter 1: 2 figures (Hình 1.1: Quy trình tổng thể, Hình 1.2: Các nhóm thông số kỹ thuật)
   - Chapter 2: 3 figures (Hình 2.1: Sơ đồ học máy hồi quy, Hình 2.2: So sánh 4 mô hình, Hình 2.3: Overfitting & 5-Fold CV)
3. Full Clickability:
   - Every TOC, Table, and Figure item has a bookmark and internal hyperlink.
4. Auto & Manual Page Numbers:
   - Embedded with PAGEREF fields for auto-update via F9, and editable run for manual typing.
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.section import WD_SECTION_START
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

sys.stdout.reconfigure(encoding='utf-8')
print("Starting generator...")
