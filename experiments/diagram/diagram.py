#!/usr/bin/env python3
"""
Script demo vẽ flowchart diagram đơn giản với xlwings
Tạo một quy trình đơn giản: Start -> Process -> Decision -> End
"""

import xlwings as xw

def create_simple_flowchart():
    """
    Tạo một flowchart đơn giản với các shapes:
    - Rectangle cho Start/End
    - Diamond cho Decision
    - Rectangle cho Process
    - Arrows để kết nối
    """
    
    # Tạo workbook mới
    wb = xw.Book()
    sheet = wb.sheets[0]
    sheet.name = "Flowchart Demo"
    
    # Định nghĩa các MSO Shape constants (từ Microsoft Office)
    # Reference: https://docs.microsoft.com/en-us/office/vba/api/office.msoshapetype
    msoShapeRectangle = 1
    msoShapeDiamond = 4
    msoShapeOval = 9
    msoShapeRoundedRectangle = 5
    
    # Định nghĩa vị trí và kích thước
    left_margin = 50
    vertical_spacing = 120
    shape_width = 150
    shape_height = 60
    
    # 1. Vẽ START shape (Rounded Rectangle - màu xanh lá)
    start_shape = sheet.shapes.api.AddShape(
        Type=msoShapeRoundedRectangle,
        Left=left_margin,
        Top=50,
        Width=shape_width,
        Height=shape_height
    )
    start_shape.TextFrame.Characters().Text = "START"
    start_shape.TextFrame.Characters().Font.Size = 14
    start_shape.TextFrame.Characters().Font.Bold = True
    start_shape.Fill.ForeColor.RGB = 0x90EE90  # Light Green
    start_shape.TextFrame.HorizontalAlignment = -4108  # xlCenter
    start_shape.TextFrame.VerticalAlignment = -4108  # xlCenter
    
    # 2. Vẽ PROCESS shape (Rectangle - màu xanh dương)
    process_top = 50 + shape_height + vertical_spacing
    process_shape = sheet.shapes.api.AddShape(
        Type=msoShapeRectangle,
        Left=left_margin,
        Top=process_top,
        Width=shape_width,
        Height=shape_height
    )
    process_shape.TextFrame.Characters().Text = "Xử lý dữ liệu"
    process_shape.TextFrame.Characters().Font.Size = 12
    process_shape.Fill.ForeColor.RGB = 0xADD8E6  # Light Blue
    process_shape.TextFrame.HorizontalAlignment = -4108
    process_shape.TextFrame.VerticalAlignment = -4108
    
    # 3. Vẽ DECISION shape (Diamond - màu vàng)
    decision_top = process_top + shape_height + vertical_spacing
    decision_shape = sheet.shapes.api.AddShape(
        Type=msoShapeDiamond,
        Left=left_margin,
        Top=decision_top,
        Width=shape_width,
        Height=shape_height
    )
    decision_shape.TextFrame.Characters().Text = "Điều kiện\nthỏa mãn?"
    decision_shape.TextFrame.Characters().Font.Size = 11
    decision_shape.Fill.ForeColor.RGB = 0xFFFFE0  # Light Yellow
    decision_shape.TextFrame.HorizontalAlignment = -4108
    decision_shape.TextFrame.VerticalAlignment = -4108
    
    # 4. Vẽ END shape (Rounded Rectangle - màu đỏ nhạt)
    end_top = decision_top + shape_height + vertical_spacing
    end_shape = sheet.shapes.api.AddShape(
        Type=msoShapeRoundedRectangle,
        Left=left_margin,
        Top=end_top,
        Width=shape_width,
        Height=shape_height
    )
    end_shape.TextFrame.Characters().Text = "END"
    end_shape.TextFrame.Characters().Font.Size = 14
    end_shape.TextFrame.Characters().Font.Bold = True
    end_shape.Fill.ForeColor.RGB = 0xFFB6C1  # Light Pink
    end_shape.TextFrame.HorizontalAlignment = -4108
    end_shape.TextFrame.VerticalAlignment = -4108
    
    # 5. Vẽ ALTERNATE PATH (ở bên phải) - cho trường hợp "No"
    alternate_left = left_margin + shape_width + 100
    alternate_shape = sheet.shapes.api.AddShape(
        Type=msoShapeRectangle,
        Left=alternate_left,
        Top=decision_top,
        Width=shape_width,
        Height=shape_height
    )
    alternate_shape.TextFrame.Characters().Text = "Xử lý\nthay thế"
    alternate_shape.TextFrame.Characters().Font.Size = 11
    alternate_shape.Fill.ForeColor.RGB = 0xFFDAB9  # Peach
    alternate_shape.TextFrame.HorizontalAlignment = -4108
    alternate_shape.TextFrame.VerticalAlignment = -4108
    
    # 6. Vẽ các CONNECTORS (Arrows)
    # Arrow từ START -> PROCESS
    connector1 = sheet.shapes.api.AddConnector(
        Type=1,  # msoConnectorStraight
        BeginX=left_margin + shape_width/2,
        BeginY=50 + shape_height,
        EndX=left_margin + shape_width/2,
        EndY=process_top
    )
    connector1.Line.EndArrowheadStyle = 3  # msoArrowheadTriangle
    connector1.Line.Weight = 2
    
    # Arrow từ PROCESS -> DECISION
    connector2 = sheet.shapes.api.AddConnector(
        Type=1,
        BeginX=left_margin + shape_width/2,
        BeginY=process_top + shape_height,
        EndX=left_margin + shape_width/2,
        EndY=decision_top
    )
    connector2.Line.EndArrowheadStyle = 3
    connector2.Line.Weight = 2
    
    # Arrow từ DECISION -> END (Yes path)
    connector3 = sheet.shapes.api.AddConnector(
        Type=1,
        BeginX=left_margin + shape_width/2,
        BeginY=decision_top + shape_height,
        EndX=left_margin + shape_width/2,
        EndY=end_top
    )
    connector3.Line.EndArrowheadStyle = 3
    connector3.Line.Weight = 2
    connector3.Line.ForeColor.RGB = 0x00FF00  # Green for Yes
    
    # Arrow từ DECISION -> ALTERNATE (No path)
    connector4 = sheet.shapes.api.AddConnector(
        Type=1,
        BeginX=left_margin + shape_width,
        BeginY=decision_top + shape_height/2,
        EndX=alternate_left,
        EndY=decision_top + shape_height/2
    )
    connector4.Line.EndArrowheadStyle = 3
    connector4.Line.Weight = 2
    connector4.Line.ForeColor.RGB = 0xFF0000  # Red for No
    
    # 7. Thêm labels cho Yes/No
    yes_label = sheet.shapes.api.AddTextbox(
        Orientation=1,
        Left=left_margin + shape_width/2 - 30,
        Top=decision_top + shape_height + 5,
        Width=50,
        Height=20
    )
    yes_label.TextFrame.Characters().Text = "Yes"
    yes_label.TextFrame.Characters().Font.Size = 10
    yes_label.TextFrame.Characters().Font.Color = 0x00FF00
    yes_label.Line.Visible = False
    
    no_label = sheet.shapes.api.AddTextbox(
        Orientation=1,
        Left=left_margin + shape_width + 10,
        Top=decision_top + shape_height/2 - 10,
        Width=50,
        Height=20
    )
    no_label.TextFrame.Characters().Text = "No"
    no_label.TextFrame.Characters().Font.Size = 10
    no_label.TextFrame.Characters().Font.Color = 0xFF0000
    no_label.Line.Visible = False
    
    # 8. Thêm title cho diagram
    title = sheet.shapes.api.AddTextbox(
        Orientation=1,
        Left=50,
        Top=10,
        Width=400,
        Height=30
    )
    title.TextFrame.Characters().Text = "Simple Flowchart Demo - Created with xlwings"
    title.TextFrame.Characters().Font.Size = 16
    title.TextFrame.Characters().Font.Bold = True
    title.TextFrame.Characters().Font.Color = 0x000080  # Navy
    title.Line.Visible = False
    
    # Lưu file
    output_path = 'flowchart_demo.xlsx'
    wb.save(output_path)
    print(f"✅ Đã tạo flowchart thành công tại: {output_path}")
    print(f"📊 File chứa {len(sheet.shapes)} shapes")
    
    # Không đóng workbook để có thể xem trong Excel nếu chạy trên Windows
    # wb.close()
    
    return output_path

if __name__ == '__main__':
    try:
        output = create_simple_flowchart()
        print("\n🎨 Diagram đã được vẽ với các thành phần:")
        print("   - START (Rounded Rectangle - xanh lá)")
        print("   - PROCESS (Rectangle - xanh dương)")
        print("   - DECISION (Diamond - vàng)")
        print("   - END (Rounded Rectangle - hồng)")
        print("   - ALTERNATE PATH (Rectangle - đào)")
        print("   - Connectors với arrows")
        print("   - Labels cho Yes/No paths")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        print("\nLưu ý: xlwings cần Excel application để chạy.")
        print("Script này sẽ hoạt động tốt nhất trên Windows/Mac với Excel đã cài đặt.")