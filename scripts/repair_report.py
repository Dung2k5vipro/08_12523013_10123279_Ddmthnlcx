# -*- coding: utf-8 -*-
"""Repair and enrich docs/baocao.docx.

The script converts pseudo-formulas to native Word equations, replaces manually
typed navigation pages with updateable Word fields, and expands Chapters 1–2.
It is intentionally idempotent: the expansion marker prevents duplicate text.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from lxml import etree


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "baocao.docx"
BACKUP = ROOT / "docs" / "baocao_before_repair.docx"
XSL = Path(r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL")
EXPANSION_MARKER = "1.7. Ý nghĩa khoa học và thực tiễn của đề tài"
ADDENDUM_MARKER = "2.19. Khả năng giải thích, độ tin cậy và giới hạn của mô hình"


def find_paragraph(doc: Document, exact: str):
    for paragraph in doc.paragraphs:
        if paragraph.text.strip() == exact:
            return paragraph
    raise ValueError(f"Không tìm thấy đoạn: {exact}")


def insert_paragraph_before(anchor, text: str = "", style: str | None = None):
    p = OxmlElement("w:p")
    anchor._p.addprevious(p)
    paragraph = anchor._parent.add_paragraph()
    paragraph._p.getparent().remove(paragraph._p)
    paragraph._p = p
    if style:
        paragraph.style = style
    if text:
        paragraph.add_run(text)
    return paragraph


def style_body(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    paragraph.paragraph_format.first_line_indent = Cm(1.0)
    paragraph.paragraph_format.line_spacing = 1.35
    paragraph.paragraph_format.space_after = Pt(6)
    for run in paragraph.runs:
        run.font.name = "Times New Roman"
        run.font.size = Pt(13)


def add_body_before(anchor, text: str):
    p = insert_paragraph_before(anchor, text, "Normal")
    style_body(p)
    return p


def add_heading_before(anchor, text: str, level: int = 2):
    p = insert_paragraph_before(anchor, text, f"Heading {level}")
    p.paragraph_format.keep_with_next = True
    return p


def add_field(paragraph, instruction: str, placeholder: str):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    begin.set(qn("w:dirty"), "true")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = f" {instruction} "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = placeholder
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, separate, text, end])


def clear_between(start, end):
    node = start._p.getnext()
    while node is not None and node is not end._p:
        nxt = node.getnext()
        node.getparent().remove(node)
        node = nxt


def replace_navigation(doc: Document):
    toc_title = find_paragraph(doc, "MỤC LỤC")
    table_title = find_paragraph(doc, "DANH MỤC BẢNG")
    figure_title = find_paragraph(doc, "DANH MỤC HÌNH ẢNH")
    abbrev_title = find_paragraph(doc, "DANH MỤC TỪ VIẾT TẮT")

    # A field can grow to several pages after updating.  Explicit page starts
    # keep the three generated lists from flowing into one another.
    for title in (table_title, figure_title, abbrev_title):
        title.paragraph_format.page_break_before = True

    clear_between(toc_title, table_title)
    toc = insert_paragraph_before(table_title)
    add_field(toc, 'TOC \\o "1-3" \\h \\z \\u', "Mục lục sẽ được cập nhật tự động khi mở tệp.")

    clear_between(table_title, figure_title)
    lot = insert_paragraph_before(figure_title)
    add_field(lot, 'TOC \\h \\z \\t "Table Caption,1"', "Danh mục bảng sẽ được cập nhật tự động khi mở tệp.")

    clear_between(figure_title, abbrev_title)
    lof = insert_paragraph_before(abbrev_title)
    add_field(lof, 'TOC \\h \\z \\t "Figure Caption,1"', "Danh mục hình sẽ được cập nhật tự động khi mở tệp.")


def ensure_caption_styles(doc: Document):
    for name in ("Table Caption", "Figure Caption"):
        if name not in doc.styles:
            style = doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        else:
            style = doc.styles[name]
        style.base_style = doc.styles["Normal"]
        style.font.name = "Times New Roman"
        style.font.size = Pt(12)
        style.font.italic = name.startswith("Figure")
        style.paragraph_format.keep_with_next = name.startswith("Table")
        style.paragraph_format.space_after = Pt(6)

    for p in doc.paragraphs:
        text = p.text.strip()
        if text.startswith("Hình ") and ":" in text and not text.startswith("Hình ảnh"):
            p.style = doc.styles["Figure Caption"]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif text.startswith("Bảng ") and ":" in text:
            p.style = doc.styles["Table Caption"]


def mathml_to_omml(mathml: str):
    transform = etree.XSLT(etree.parse(str(XSL)))
    return transform(etree.fromstring(mathml.encode("utf-8"))).getroot()


def set_equation(paragraph, mathml: str):
    for child in list(paragraph._p):
        if child.tag != qn("w:pPr"):
            paragraph._p.remove(child)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before = Pt(8)
    paragraph.paragraph_format.space_after = Pt(8)
    paragraph._p.append(mathml_to_omml(mathml))


def replace_formulas(doc: Document):
    formulas = {
        "y_pred = w_0 + w_1 * x_1 + w_2 * x_2 + ... + w_p * x_p": """
          <math xmlns="http://www.w3.org/1998/Math/MathML"><mrow>
          <mover><mi>y</mi><mo>^</mo></mover><mo>=</mo><msub><mi>w</mi><mn>0</mn></msub><mo>+</mo>
          <munderover><mo>∑</mo><mrow><mi>j</mi><mo>=</mo><mn>1</mn></mrow><mi>p</mi></munderover>
          <msub><mi>w</mi><mi>j</mi></msub><msub><mi>x</mi><mi>j</mi></msub></mrow></math>""",
        "MAE = (1 / n) * sum(|y_i - y_pred_i|)": """
          <math xmlns="http://www.w3.org/1998/Math/MathML"><mrow><mi>MAE</mi><mo>=</mo>
          <mfrac><mn>1</mn><mi>n</mi></mfrac><munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>n</mi></munderover>
          <mfenced open="|" close="|"><mrow><msub><mi>y</mi><mi>i</mi></msub><mo>−</mo><msub><mover><mi>y</mi><mo>^</mo></mover><mi>i</mi></msub></mrow></mfenced></mrow></math>""",
        "RMSE = sqrt((1 / n) * sum((y_i - y_pred_i)^2))": """
          <math xmlns="http://www.w3.org/1998/Math/MathML"><mrow><mi>RMSE</mi><mo>=</mo><msqrt><mrow>
          <mfrac><mn>1</mn><mi>n</mi></mfrac><munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>n</mi></munderover>
          <msup><mfenced><mrow><msub><mi>y</mi><mi>i</mi></msub><mo>−</mo><msub><mover><mi>y</mi><mo>^</mo></mover><mi>i</mi></msub></mrow></mfenced><mn>2</mn></msup></mrow></msqrt></mrow></math>""",
        "R² = 1 - [sum((y_i - y_pred_i)^2) / sum((y_i - y_mean)^2)]": """
          <math xmlns="http://www.w3.org/1998/Math/MathML"><mrow><msup><mi>R</mi><mn>2</mn></msup><mo>=</mo><mn>1</mn><mo>−</mo>
          <mfrac><mrow><munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>n</mi></munderover><msup><mfenced><mrow><msub><mi>y</mi><mi>i</mi></msub><mo>−</mo><msub><mover><mi>y</mi><mo>^</mo></mover><mi>i</mi></msub></mrow></mfenced><mn>2</mn></msup></mrow>
          <mrow><munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>n</mi></munderover><msup><mfenced><mrow><msub><mi>y</mi><mi>i</mi></msub><mo>−</mo><mover><mi>y</mi><mo>¯</mo></mover></mrow></mfenced><mn>2</mn></msup></mrow></mfrac></mrow></math>""",
    }
    for p in doc.paragraphs:
        key = p.text.strip()
        if key in formulas:
            set_equation(p, formulas[key])

    # MSE was mentioned but missing from the original report.
    if len(doc._element.body.findall(".//" + qn("m:oMath"))) >= 5:
        return
    rmse_label = find_paragraph(doc, "- Sai số bình phương trung bình (MSE) & Căn bậc hai sai số bình phương trung bình (RMSE):")
    rmse_formula = rmse_label._p.getnext().getnext()
    mse = OxmlElement("w:p")
    rmse_formula.addprevious(mse)
    dummy = doc.add_paragraph()
    dummy._p.getparent().remove(dummy._p)
    dummy._p = mse
    set_equation(dummy, """<math xmlns="http://www.w3.org/1998/Math/MathML"><mrow><mi>MSE</mi><mo>=</mo>
      <mfrac><mn>1</mn><mi>n</mi></mfrac><munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>n</mi></munderover>
      <msup><mfenced><mrow><msub><mi>y</mi><mi>i</mi></msub><mo>−</mo><msub><mover><mi>y</mi><mo>^</mo></mover><mi>i</mi></msub></mrow></mfenced><mn>2</mn></msup></mrow></math>""")


CHAPTER_1 = [
    ("h2", "1.7. Ý nghĩa khoa học và thực tiễn của đề tài"),
    ("p", "Về phương diện khoa học, đề tài là một trường hợp nghiên cứu điển hình cho quy trình giải quyết bài toán hồi quy trên dữ liệu hỗn hợp, trong đó các biến số như năm sản xuất, dung tích động cơ và số xi-lanh đồng thời tồn tại với các biến phân loại có nhiều giá trị như hãng xe, lớp xe, hộp số và loại nhiên liệu. Việc lựa chọn cách biểu diễn phù hợp cho từng nhóm biến giúp làm rõ mối liên hệ giữa bản chất dữ liệu và giả định của thuật toán. Qua đó, báo cáo không chỉ dừng ở việc tìm mô hình có điểm số cao mà còn giải thích vì sao một mô hình tuyến tính, mô hình dựa trên khoảng cách, cây quyết định và mô hình biên hỗ trợ tạo ra các sai số khác nhau trên cùng một tập dữ liệu."),
    ("p", "Một ý nghĩa khoa học khác là việc tuân thủ nguyên tắc tách biệt dữ liệu huấn luyện và dữ liệu kiểm tra trong toàn bộ chu trình xây dựng mô hình. Các phép học tham số của bộ chuẩn hóa, từ điển mã hóa biến phân loại và quá trình chọn siêu tham số đều chỉ sử dụng tập huấn luyện. Cách tổ chức này giúp kết quả đánh giá phản ánh đúng năng lực khái quát hóa thay vì phản ánh khả năng ghi nhớ dữ liệu. Đây là yêu cầu nền tảng nhưng thường bị bỏ qua trong các bài toán thực hành, đặc biệt khi các thao tác tiền xử lý được thực hiện thủ công trước bước chia dữ liệu."),
    ("p", "Về phương diện thực tiễn, một ước lượng tiêu hao nhiên liệu đáng tin cậy hỗ trợ người mua so sánh chi phí vận hành giữa các cấu hình xe trước khi ra quyết định. Doanh nghiệp vận tải có thể sử dụng giá trị dự đoán như một tham chiếu ban đầu khi xây dựng ngân sách nhiên liệu, lựa chọn phương tiện cho từng tuyến và nhận diện những cấu hình có nguy cơ tiêu thụ cao. Đối với cơ quan quản lý, kết quả phân tích góp phần chỉ ra các nhóm thông số kỹ thuật liên quan mạnh đến nhu cầu năng lượng, từ đó hỗ trợ hoạt động truyền thông về sử dụng phương tiện tiết kiệm và giảm phát thải."),
    ("p", "Tuy nhiên, giá trị dự đoán của hệ thống phải được hiểu là mức tham chiếu dựa trên điều kiện kiểm định và đặc tính kỹ thuật, không thay thế số đo trong điều kiện vận hành thực tế. Mức tiêu thụ còn chịu ảnh hưởng của tải trọng, mật độ giao thông, địa hình, thời tiết, tình trạng bảo dưỡng, áp suất lốp và hành vi người lái. Việc nêu rõ giới hạn này giúp tránh diễn giải quá mức kết quả mô hình và định hướng đúng cho các bước thu thập dữ liệu mở rộng trong tương lai."),
    ("h2", "1.8. Những thách thức của bài toán"),
    ("p", "Thách thức đầu tiên nằm ở tính không đồng nhất theo thời gian. Bộ dữ liệu trải dài gần ba thập kỷ, trong khi tiêu chuẩn kiểm định, công nghệ phun nhiên liệu, tăng áp, điều khiển van, hộp số và chiến lược giảm phát thải liên tục thay đổi. Hai phương tiện có thông số dung tích và số xi-lanh giống nhau nhưng khác năm sản xuất có thể đạt hiệu suất rất khác. Vì vậy, năm sản xuất không chỉ là thông tin định danh mà còn đóng vai trò biến đại diện cho tiến bộ công nghệ và thay đổi quy chuẩn."),
    ("p", "Thách thức thứ hai là sự đa dạng và mất cân bằng của các biến phân loại. Một số hãng và lớp xe xuất hiện với tần suất lớn, trong khi các cấu hình hiếm chỉ có ít quan sát. Nếu mô hình quá phụ thuộc vào nhóm phổ biến, sai số đối với nhóm hiếm có thể cao dù chỉ số trung bình toàn tập vẫn tốt. Kỹ thuật mã hóa phải xử lý được giá trị mới khi triển khai, đồng thời tránh tạo ra thứ tự giả giữa các nhãn danh định. Đây là lý do One-Hot Encoding với cơ chế bỏ qua nhãn chưa biết được lựa chọn trong Pipeline."),
    ("p", "Thách thức thứ ba là quan hệ giữa đặc trưng và mục tiêu không hoàn toàn tuyến tính. Dung tích động cơ và số xi-lanh có xu hướng đồng biến với mức tiêu hao nhưng tác động còn phụ thuộc lớp xe, hộp số, nhiên liệu và giai đoạn công nghệ. Hiệu ứng tương tác khiến một đường hồi quy duy nhất khó mô tả đầy đủ toàn bộ không gian dữ liệu. Việc so sánh nhiều họ thuật toán là cần thiết để cân bằng khả năng biểu diễn phi tuyến, độ ổn định, tốc độ suy luận và mức độ dễ giải thích."),
    ("p", "Thách thức cuối cùng là rò rỉ dữ liệu. Các cột tiêu hao trong thành phố, trên đường trường và phát thải CO2 có quan hệ trực tiếp với biến tiêu hao kết hợp; giữ lại các cột này có thể tạo ra điểm số gần như hoàn hảo nhưng không phản ánh tình huống dự đoán từ thông số thiết kế. Báo cáo vì thế xem kiểm soát rò rỉ là một quyết định thiết kế cốt lõi, không phải một thao tác làm sạch phụ trợ."),
    ("h2", "1.9. Đóng góp dự kiến của đề tài"),
    ("p", "Đề tài cung cấp một quy trình có khả năng tái lập từ dữ liệu thô đến dịch vụ dự đoán. Quy trình bao gồm kiểm tra chất lượng dữ liệu, phân tích khám phá, lựa chọn đặc trưng, đóng gói tiền xử lý và mô hình trong cùng Pipeline, tinh chỉnh bằng kiểm định chéo, đánh giá trên tập kiểm tra độc lập và lưu phiên bản mô hình. Mỗi bước đều có đầu vào, đầu ra và tiêu chí kiểm tra rõ ràng, nhờ đó kết quả có thể được kiểm chứng hoặc mở rộng mà không phụ thuộc vào các thao tác thủ công khó lặp lại."),
    ("p", "Đóng góp thứ hai là phần đối sánh bốn mô hình đại diện cho bốn cách tiếp cận khác nhau: mô hình tham số tuyến tính, mô hình phân hoạch theo luật, mô hình dựa trên lân cận và mô hình cực đại hóa biên. Việc đánh giá đồng thời bằng MAE, MSE, RMSE, R² và thời gian suy luận tạo ra góc nhìn nhiều chiều hơn so với chỉ sử dụng một điểm số. Kết quả lựa chọn cuối cùng vì thế dựa trên cả độ chính xác, độ ổn định và yêu cầu triển khai."),
    ("p", "Đóng góp thứ ba là hệ thống phần mềm nhiều tầng kết nối mô hình học máy với giao diện người dùng. Mô hình được tách khỏi lớp nghiệp vụ thông qua dịch vụ FastAPI; lớp backend kiểm tra dữ liệu và điều phối yêu cầu; lớp frontend thu thập thông tin xe và trình bày kết quả. Kiến trúc tách biệt giúp từng thành phần có thể kiểm thử, thay thế hoặc mở rộng độc lập, đồng thời phản ánh đúng quy trình đưa một mô hình từ môi trường nghiên cứu sang ứng dụng."),
    ("h2", "1.10. Cấu trúc báo cáo"),
    ("p", "Ngoài phần mở đầu và các danh mục, báo cáo gồm năm chương. Chương 1 trình bày bối cảnh, mục tiêu, phạm vi, phương pháp và đóng góp của đề tài. Chương 2 hệ thống hóa cơ sở lý thuyết về học có giám sát, hồi quy, tiền xử lý, bốn thuật toán, các chỉ số đánh giá và kiểm định chéo. Chương 3 mô tả bộ dữ liệu, phân tích khám phá và quy trình chuẩn bị dữ liệu. Chương 4 trình bày thiết kế thực nghiệm, tinh chỉnh siêu tham số, kết quả đối sánh và lựa chọn mô hình. Chương 5 mô tả kiến trúc hệ thống, tích hợp mô hình và các kịch bản kiểm thử. Phần cuối tổng hợp kết luận, giới hạn và hướng phát triển."),
]


CHAPTER_2 = [
    ("h2", "2.13. Biểu diễn dữ liệu và tiền xử lý trong học máy"),
    ("p", "Mô hình học máy chỉ tiếp nhận dữ liệu dưới dạng số, trong khi bộ dữ liệu xe chứa đồng thời biến định lượng và biến định tính. Với biến định lượng, thang đo giữa năm sản xuất, dung tích động cơ và số xi-lanh khác nhau đáng kể. Nếu sử dụng trực tiếp trong thuật toán dựa trên khoảng cách, biến có miền giá trị lớn có thể chi phối khoảng cách tổng thể dù chưa chắc quan trọng hơn về mặt dự đoán. Chuẩn hóa đưa các biến về thang đo tương thích, giúp quá trình tối ưu ổn định và làm cho đóng góp của từng chiều dữ liệu cân bằng hơn."),
    ("p", "StandardScaler biến đổi mỗi giá trị bằng cách trừ trung bình và chia cho độ lệch chuẩn được ước lượng trên tập huấn luyện. Sau biến đổi, biến có trung bình xấp xỉ bằng không và độ lệch chuẩn xấp xỉ bằng một. RobustScaler thay trung bình và độ lệch chuẩn bằng trung vị và khoảng tứ phân vị nên ít nhạy hơn với ngoại lệ. Việc lựa chọn bộ chuẩn hóa phải dựa trên phân bố thực nghiệm; quan trọng hơn, mọi tham số chuẩn hóa phải được học trong từng fold huấn luyện để không truyền thông tin từ fold kiểm định sang mô hình."),
    ("p", "Với biến phân loại danh định, mã hóa One-Hot tạo một cột nhị phân cho mỗi giá trị. Cách biểu diễn này không áp đặt quan hệ thứ tự giả, chẳng hạn không ngầm coi hãng xe A nhỏ hơn hoặc lớn hơn hãng xe B. Đổi lại, số chiều có thể tăng mạnh với biến có nhiều giá trị. Cơ chế handle_unknown='ignore' bảo đảm một nhãn mới khi suy luận không làm hỏng toàn bộ Pipeline; nhãn đó được biểu diễn bằng vector không tại nhóm cột tương ứng và mô hình vẫn có thể dựa vào các đặc trưng còn lại."),
    ("p", "ColumnTransformer cho phép áp dụng các chuỗi xử lý riêng lên từng nhóm cột rồi ghép kết quả thành một ma trận đặc trưng thống nhất. Khi ColumnTransformer được đặt cùng thuật toán trong Pipeline, lời gọi fit, transform và predict tuân theo đúng một trình tự ở cả huấn luyện lẫn triển khai. Thiết kế này loại bỏ sai lệch thường gặp khi mã nghiên cứu và mã phục vụ dự đoán sử dụng các bước xử lý khác nhau."),
    ("h2", "2.14. Hàm mất mát, tối ưu hóa và chính quy hóa"),
    ("p", "Hàm mất mát định lượng mức độ khác biệt giữa giá trị thực và giá trị dự đoán trên từng mẫu; hàm mục tiêu thường là trung bình hoặc tổng của các mất mát, có thể cộng thêm thành phần chính quy hóa. Trong hồi quy tuyến tính theo bình phương tối thiểu, bình phương phần dư tạo ra một bài toán lồi và phạt mạnh các sai số lớn. Tính chất khả vi giúp nghiệm có thể được tìm bằng công thức đóng hoặc các phương pháp tối ưu số. Tuy nhiên, việc bình phương cũng làm mô hình nhạy hơn với ngoại lệ."),
    ("p", "Chính quy hóa kiểm soát độ phức tạp bằng cách phạt độ lớn tham số. Phạt L2 khuyến khích các hệ số nhỏ và phân bố ảnh hưởng trên nhiều biến; phạt L1 có thể đưa một số hệ số về đúng không và tạo hiệu ứng chọn đặc trưng. Trong SVR, tham số C đảm nhiệm vai trò tương tự thông qua mức phạt dành cho các điểm nằm ngoài dải epsilon. C quá lớn khiến mô hình cố giảm sai số huấn luyện và tăng nguy cơ quá khớp; C quá nhỏ tạo mô hình trơn hơn nhưng có thể bỏ sót cấu trúc quan trọng."),
    ("p", "Khái niệm đánh đổi độ chệch–phương sai giải thích vì sao mô hình phức tạp hơn không mặc nhiên tốt hơn. Mô hình có độ chệch cao tạo sai số có hệ thống vì giả định quá đơn giản; mô hình có phương sai cao thay đổi mạnh theo mẫu huấn luyện và dễ học cả nhiễu. Mục tiêu thực tế là tìm vùng cân bằng nơi sai số trên dữ liệu chưa thấy đạt thấp và ổn định, thay vì tối thiểu hóa tuyệt đối sai số huấn luyện."),
    ("h2", "2.15. Cơ sở toán học của các mô hình được khảo sát"),
    ("h3", "2.15.1. Hồi quy tuyến tính và giả định mô hình"),
    ("p", "Hồi quy tuyến tính biểu diễn kỳ vọng của biến mục tiêu như tổ hợp tuyến tính của các đặc trưng sau biến đổi. Các giả định thường được xem xét gồm tính tuyến tính theo tham số, kỳ vọng phần dư bằng không, phương sai phần dư tương đối ổn định, các quan sát độc lập và mức đa cộng tuyến không quá nghiêm trọng. Trong bài toán dự đoán, vi phạm một phần các giả định không nhất thiết làm mô hình mất hoàn toàn giá trị, nhưng có thể làm giảm khả năng giải thích hệ số và khiến khoảng tin cậy thiếu chính xác."),
    ("p", "Sau One-Hot Encoding, mỗi hệ số của biến phân loại phản ánh mức thay đổi dự kiến so với nhóm tham chiếu khi các đặc trưng khác được giữ cố định. Hệ số của dung tích động cơ hoặc số xi-lanh phản ánh tác động cận biên trong phạm vi giả định tuyến tính. Do hai biến này tương quan mạnh, độ lớn từng hệ số có thể không ổn định dù tổng năng lực dự đoán vẫn chấp nhận được. Vì vậy, diễn giải phải kết hợp hiểu biết miền và kiểm tra đa cộng tuyến thay vì xem hệ số là quan hệ nhân quả."),
    ("h3", "2.15.2. Cây quyết định cho hồi quy"),
    ("p", "Tại mỗi nút, cây quyết định xét các ngưỡng chia ứng viên và chọn phép chia làm giảm bất thuần hồi quy nhiều nhất. Với tiêu chí sai số bình phương, độ bất thuần tại một nút bằng trung bình bình phương độ lệch của các giá trị mục tiêu so với trung bình nút. Quá trình phân chia lặp lại tạo ra các vùng chữ nhật trong không gian đặc trưng; dự đoán của một vùng bằng trung bình mục tiêu của các mẫu huấn luyện rơi vào lá tương ứng."),
    ("p", "Cây có ưu điểm mô hình hóa tự nhiên quan hệ phi tuyến và tương tác mà không yêu cầu chuẩn hóa. Tuy nhiên, các ngưỡng chia được chọn tham lam nên một thay đổi nhỏ trong dữ liệu có thể tạo cấu trúc cây khác. Các siêu tham số max_depth, min_samples_split và min_samples_leaf trực tiếp kiểm soát kích thước vùng phân hoạch. Giới hạn độ sâu hoặc yêu cầu nhiều mẫu hơn tại lá làm tăng độ chệch nhưng giảm phương sai và thường cải thiện khả năng khái quát hóa."),
    ("h3", "2.15.3. K láng giềng gần nhất cho hồi quy"),
    ("p", "KNN không xây dựng một hàm tham số cố định trong giai đoạn fit mà lưu tập huấn luyện đã biến đổi. Khi dự đoán, thuật toán xác định K điểm gần nhất theo một thước đo khoảng cách và tổng hợp mục tiêu của chúng. Với trọng số đều, mọi láng giềng đóng góp như nhau; với trọng số nghịch đảo khoảng cách, các điểm gần có ảnh hưởng lớn hơn. Giá trị K nhỏ tạo đường dự đoán linh hoạt nhưng nhạy nhiễu, còn K lớn làm kết quả trơn hơn nhưng có thể làm mờ cấu trúc cục bộ."),
    ("p", "Hiệu năng của KNN suy giảm khi số chiều tăng vì khoảng cách giữa các điểm có xu hướng trở nên kém phân biệt, hiện tượng thường gọi là lời nguyền số chiều. One-Hot Encoding các biến nhiều giá trị làm vấn đề này đáng chú ý hơn. Do đó, KNN cần được đánh giá cùng lựa chọn thước đo, số láng giềng, cơ chế trọng số và cách chuẩn hóa. Chi phí suy luận cũng tăng theo số mẫu huấn luyện nếu không có cấu trúc tìm kiếm lân cận phù hợp."),
    ("h3", "2.15.4. Support Vector Regression và hàm nhân"),
    ("p", "SVR tìm một hàm đủ phẳng sao cho nhiều điểm dữ liệu nằm trong ống sai số có bán kính epsilon. Sai số bên trong ống không bị phạt; chỉ phần vượt ra ngoài mới đóng góp vào hàm mục tiêu. Cơ chế này khiến mô hình ít phản ứng với các dao động nhỏ và tập trung vào những sai lệch có ý nghĩa. Các mẫu nằm trên hoặc ngoài biên trở thành vector hỗ trợ và quyết định hình dạng hàm dự đoán."),
    ("p", "Hàm nhân RBF đo độ tương đồng giảm theo bình phương khoảng cách giữa hai điểm trong không gian đặc trưng. Tham số gamma lớn làm vùng ảnh hưởng của mỗi điểm hẹp, tạo hàm linh hoạt nhưng dễ quá khớp; gamma nhỏ tạo bề mặt trơn hơn. Ba tham số C, gamma và epsilon tương tác chặt chẽ nên không nên tinh chỉnh riêng lẻ. GridSearchCV đánh giá các tổ hợp trong cùng quy trình tiền xử lý giúp lựa chọn cấu hình trên cơ sở năng lực khái quát hóa trung bình."),
    ("h2", "2.16. Đánh giá mô hình hồi quy theo nhiều tiêu chí"),
    ("p", "MAE là trung bình độ lớn tuyệt đối của phần dư nên có cùng đơn vị với mục tiêu và dễ diễn giải: MAE bằng 0,5 L/100 km nghĩa là dự đoán lệch trung bình khoảng 0,5 L/100 km. Do mức phạt tăng tuyến tính, MAE ít bị chi phối bởi một số sai số cực lớn hơn MSE. Chỉ số này phù hợp khi chi phí của sai số tăng gần tuyến tính và người sử dụng cần một đại lượng trực quan."),
    ("p", "MSE bình phương phần dư trước khi lấy trung bình, vì vậy các dự đoán lệch xa bị phạt mạnh. RMSE là căn bậc hai của MSE và trở lại cùng đơn vị với biến mục tiêu. So sánh MAE với RMSE cung cấp thông tin về đuôi phân bố sai số: nếu RMSE lớn hơn MAE đáng kể, mô hình có thể tồn tại một nhóm dự đoán sai nhiều cần được phân tích riêng theo lớp xe, loại nhiên liệu hoặc giai đoạn sản xuất."),
    ("p", "R² đo tỷ lệ biến thiên của mục tiêu được mô hình giải thích so với dự đoán hằng bằng trung bình. R² bằng một tương ứng dự đoán hoàn hảo; bằng không nghĩa là không tốt hơn mô hình trung bình trên tập đánh giá; giá trị âm có thể xuất hiện khi mô hình kém hơn mốc này. R² không cho biết độ lớn sai số theo đơn vị thực tế, nên phải được báo cáo cùng MAE hoặc RMSE. Một R² cao vẫn có thể che giấu sai số lớn nếu miền biến mục tiêu rất rộng."),
    ("p", "Ngoài điểm số tổng hợp, đồ thị Actual–Predicted và đồ thị phần dư giúp phát hiện cấu trúc mà chỉ số vô hướng bỏ qua. Các điểm Actual–Predicted lý tưởng nằm gần đường chéo; phần dư lý tưởng phân bố ngẫu nhiên quanh không và không tạo hình phễu hay đường cong. Xu hướng cong gợi ý quan hệ chưa được mô hình hóa, hình phễu gợi ý phương sai thay đổi, còn các cụm riêng biệt có thể cho thấy sai số phụ thuộc vào một nhóm phương tiện cụ thể."),
    ("h2", "2.17. Kiểm định chéo, lựa chọn siêu tham số và tránh rò rỉ"),
    ("p", "Trong K-Fold Cross Validation, tập huấn luyện được chia thành K phần gần bằng nhau. Mỗi lượt dùng một phần làm fold kiểm định và K−1 phần còn lại để fit toàn bộ Pipeline. Sau K lượt, điểm trung bình ước lượng hiệu năng và độ lệch chuẩn phản ánh mức ổn định giữa các cách chia. Với K=5, mô hình được huấn luyện năm lần cho mỗi cấu hình, tạo cân bằng hợp lý giữa độ tin cậy và chi phí tính toán."),
    ("p", "Tập kiểm tra cuối cùng không được dùng để chọn thuật toán, chọn đặc trưng, chọn siêu tham số hoặc quyết định dừng thử nghiệm. Nếu liên tục điều chỉnh theo kết quả test, tập test dần trở thành một phần của quá trình huấn luyện và ước lượng hiệu năng sẽ lạc quan. Quy trình đúng sử dụng Cross Validation trên tập train để ra quyết định, sau đó chỉ đánh giá một lần trên tập test đã được giữ độc lập."),
    ("p", "Rò rỉ trong tiền xử lý có thể xảy ra tinh vi khi bộ chuẩn hóa hoặc bộ mã hóa được fit trên toàn bộ dữ liệu trước khi chia fold. Khi đó, thống kê của các quan sát kiểm định đã ảnh hưởng đến biểu diễn của tập huấn luyện. Đặt mọi phép biến đổi trong Pipeline khiến GridSearchCV tự fit lại chúng trên từng fold, loại bỏ đường truyền thông tin này và bảo đảm điểm số phản ánh đúng tình huống triển khai."),
    ("h2", "2.18. Từ mô hình nghiên cứu đến hệ thống dự đoán"),
    ("p", "Một mô hình đạt điểm cao trong notebook chưa đủ để trở thành thành phần phần mềm đáng tin cậy. Gói mô hình phải chứa đồng thời bộ tiền xử lý, thuật toán, danh sách trường đầu vào và thông tin phiên bản. Dịch vụ suy luận cần kiểm tra kiểu dữ liệu, miền giá trị và danh mục hợp lệ trước khi gọi predict. Cách đóng gói này ngăn hiện tượng lệch huấn luyện–phục vụ, trong đó dữ liệu triển khai được biến đổi khác dữ liệu đã dùng để huấn luyện."),
    ("p", "Khả năng tái lập còn đòi hỏi cố định hạt giống ngẫu nhiên khi phù hợp, ghi nhận phiên bản thư viện, lưu cấu hình siêu tham số và định nghĩa rõ đơn vị đầu vào–đầu ra. Hệ thống cần theo dõi lỗi, thời gian phản hồi và phân bố yêu cầu. Khi dữ liệu thực tế thay đổi đáng kể so với dữ liệu lịch sử, chất lượng mô hình có thể suy giảm do dịch chuyển dữ liệu; khi đó cần đánh giá lại, cập nhật dữ liệu và phát hành phiên bản mô hình mới theo quy trình có kiểm soát."),
    ("p", "Cuối cùng, kết quả dự đoán cần được trình bày kèm ngữ cảnh sử dụng. Giao diện phải nêu rõ đơn vị L/100 km, phân biệt giá trị ước lượng với số đo thực tế và phản hồi rõ khi dữ liệu đầu vào không hợp lệ. Những yêu cầu này liên kết trực tiếp cơ sở lý thuyết với thiết kế hệ thống ở Chương 5, đồng thời bảo đảm sản phẩm không chỉ đúng về thuật toán mà còn nhất quán, dễ sử dụng và có khả năng bảo trì."),
]


CHAPTER_2_ADDENDUM = [
    ("h2", "2.19. Khả năng giải thích, độ tin cậy và giới hạn của mô hình"),
    ("p", "Khả năng giải thích cho biết con người có thể hiểu được những yếu tố nào dẫn tới một dự đoán cụ thể và mô hình phản ứng ra sao khi đầu vào thay đổi. Hồi quy tuyến tính có ưu thế vì dấu và độ lớn hệ số cung cấp một mô tả trực tiếp sau khi đã xét cách mã hóa và chuẩn hóa. Cây quyết định có thể được diễn giải thông qua chuỗi điều kiện từ nút gốc đến nút lá. Ngược lại, KNN và SVR thường khó giải thích toàn cục hơn vì dự đoán phụ thuộc vào cấu trúc lân cận hoặc quan hệ trong không gian đặc trưng do hàm nhân tạo ra. Do đó, lựa chọn mô hình không chỉ phụ thuộc sai số mà còn phụ thuộc mức minh bạch mà bối cảnh sử dụng yêu cầu."),
    ("p", "Có thể bổ sung các kỹ thuật giải thích bất khả tri mô hình như permutation importance hoặc phân tích độ nhạy. Permutation importance đo mức suy giảm điểm số khi hoán vị ngẫu nhiên một đặc trưng, qua đó ước lượng mức thông tin dự đoán mà đặc trưng mang lại. Phân tích độ nhạy giữ cố định phần lớn đầu vào và thay đổi một biến trong miền hợp lệ để quan sát xu hướng dự đoán. Các kết quả này phải được diễn giải thận trọng khi các biến tương quan mạnh, bởi hai biến có thể thay thế thông tin cho nhau và làm độ quan trọng riêng lẻ bị đánh giá thấp."),
    ("p", "Độ tin cậy của mô hình không đồng nghĩa với một điểm số cao trên một lần chia dữ liệu. Một mô hình đáng tin cậy cần duy trì hiệu năng tương đối ổn định giữa các fold, giữa các nhóm xe và giữa các giai đoạn sản xuất. Vì vậy, ngoài trung bình MAE, nên xem độ lệch chuẩn của điểm kiểm định chéo và phân rã sai số theo lớp xe, loại nhiên liệu hoặc khoảng dung tích động cơ. Nếu một nhóm nhỏ có sai số cao bất thường, chỉ số trung bình toàn cục có thể che khuất rủi ro sử dụng đối với chính nhóm đó."),
    ("p", "Bộ dữ liệu lịch sử phản ánh phạm vi phương tiện đã được kiểm định, vì vậy mô hình chủ yếu thực hiện nội suy trong miền đã quan sát. Một cấu hình xe hoàn toàn mới, chẳng hạn công nghệ truyền động hoặc loại nhiên liệu chưa từng xuất hiện, có thể nằm ngoài phân bố huấn luyện. Cơ chế xử lý nhãn chưa biết giúp hệ thống không phát sinh lỗi kỹ thuật nhưng không bảo đảm dự đoán chính xác. Hệ thống triển khai nên phát hiện giá trị ngoài miền hợp lý, cảnh báo người dùng và ghi nhận các trường hợp này để đánh giá lại khi cập nhật mô hình."),
    ("p", "Các chỉ số MAE và RMSE trong báo cáo là ước lượng điểm, chưa biểu diễn trực tiếp khoảng bất định quanh từng dự đoán. Trong hướng phát triển, có thể xây dựng khoảng dự đoán bằng bootstrap, conformal prediction hoặc mô hình xác suất. Khoảng dự đoán rộng cho biết trường hợp đầu vào ít tương đồng với dữ liệu huấn luyện hoặc bản thân quá trình có mức biến thiên lớn. Cung cấp đồng thời giá trị trung tâm và khoảng bất định giúp người sử dụng ra quyết định thận trọng hơn so với chỉ nhận một con số duy nhất."),
    ("p", "Cuối cùng, quan hệ thống kê mà mô hình học được không tự động trở thành quan hệ nhân quả. Ví dụ, hãng xe hoặc năm sản xuất có thể đại diện cho nhiều yếu tố công nghệ chưa được đo trực tiếp; thay đổi riêng nhãn hãng trong dữ liệu đầu vào không có nghĩa sẽ làm mức tiêu hao thực tế thay đổi theo đúng chênh lệch dự đoán. Kết quả của đề tài phù hợp cho mục tiêu ước lượng và so sánh trong phạm vi dữ liệu, nhưng mọi kết luận về nguyên nhân cần một thiết kế nghiên cứu riêng có khả năng kiểm soát yếu tố gây nhiễu."),
]


def insert_expansion(doc: Document):
    if any(p.text.strip() == EXPANSION_MARKER for p in doc.paragraphs):
        return
    chapter_2 = find_paragraph(doc, "CHƯƠNG 2: CƠ SỞ LÝ THUYẾT")
    for kind, text in CHAPTER_1:
        if kind == "p":
            add_body_before(chapter_2, text)
        else:
            add_heading_before(chapter_2, text, int(kind[-1]))

    chapter_3 = find_paragraph(doc, "CHƯƠNG 3: DỮ LIỆU VÀ TIỀN XỬ LÝ")
    for kind, text in CHAPTER_2:
        if kind == "p":
            add_body_before(chapter_3, text)
        else:
            add_heading_before(chapter_3, text, int(kind[-1]))


def insert_addendum(doc: Document):
    if any(p.text.strip() == ADDENDUM_MARKER for p in doc.paragraphs):
        return
    chapter_3 = find_paragraph(doc, "CHƯƠNG 3: DỮ LIỆU VÀ TIỀN XỬ LÝ")
    for kind, text in CHAPTER_2_ADDENDUM:
        if kind == "p":
            add_body_before(chapter_3, text)
        else:
            add_heading_before(chapter_3, text, int(kind[-1]))


def insert_only_allowed_sections(doc: Document):
    """Expand only 1.1 and 1.5 without changing the report outline."""
    section_1_2 = find_paragraph(doc, "1.2. Mục tiêu đề tài")
    section_1_6 = find_paragraph(doc, "1.6. Phương pháp tiếp cận")

    # Context, motivation, practical meaning, challenges and expected value all
    # belong to the rationale in 1.1. Heading records are deliberately ignored.
    reason_texts = [text for kind, text in CHAPTER_1 if kind == "p"]
    for text in reason_texts:
        add_body_before(section_1_2, text)

    # Detailed theory/work packages are presented as the work to be carried out
    # in 1.5. No new heading or subheading is introduced.
    work_intro = (
        "Để cụ thể hóa lộ trình trên, nội dung thực hiện được triển khai thành các "
        "nhóm công việc liên kết chặt chẽ từ cơ sở lý thuyết, chuẩn bị dữ liệu, xây "
        "dựng mô hình đến đánh giá và tích hợp hệ thống. Chi tiết của từng nhóm "
        "công việc được trình bày như sau:"
    )
    add_body_before(section_1_6, work_intro)
    work_texts = [text for kind, text in CHAPTER_2 + CHAPTER_2_ADDENDUM if kind == "p"]
    for text in work_texts:
        add_body_before(section_1_6, text)


def set_update_fields(doc: Document):
    settings = doc.settings._element
    update = settings.find(qn("w:updateFields"))
    if update is None:
        update = OxmlElement("w:updateFields")
        settings.append(update)
    update.set(qn("w:val"), "true")

    for section in doc.sections:
        for container in (section.header, section.footer):
            for p in container.paragraphs:
                for fld in p._p.findall(".//" + qn("w:fldChar")):
                    if fld.get(qn("w:fldCharType")) == "begin":
                        fld.set(qn("w:dirty"), "true")


def main():
    if not BACKUP.exists():
        shutil.copy2(REPORT, BACKUP)
    # Always rebuild from the untouched backup so the original heading
    # structure is preserved exactly.
    doc = Document(BACKUP)
    insert_only_allowed_sections(doc)
    ensure_caption_styles(doc)
    replace_navigation(doc)
    replace_formulas(doc)
    set_update_fields(doc)
    doc.core_properties.title = "Xây dựng hệ thống dự đoán mức tiêu hao nhiên liệu xe"
    doc.core_properties.subject = "Báo cáo bài tập lớn Học máy cơ bản"
    doc.save(REPORT)
    print(f"Đã sửa: {REPORT}")
    print(f"Bản sao trước khi sửa: {BACKUP}")


if __name__ == "__main__":
    main()
