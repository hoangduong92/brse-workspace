#!/usr/bin/env python3
"""
Script để reverse engineering diagram từ Excel
Đọc tất cả thông tin về shapes: vị trí, kích thước, màu sắc, text, etc.
"""

import xlwings as xw
import json

def get_rgb_from_long(rgb_long):
    """Chuyển đổi RGB long integer sang hex color"""
    try:
        # RGB được lưu dạng BGR trong COM
        b = (rgb_long >> 16) & 0xFF
        g = (rgb_long >> 8) & 0xFF
        r = rgb_long & 0xFF
        return f"#{r:02X}{g:02X}{b:02X}"
    except:
        return None

def get_shape_type_name(shape_type):
    """Chuyển đổi shape type number sang tên"""
    shape_types = {
        1: "Rectangle",
        2: "Rounded Rectangle", 
        3: "Ellipse/Oval",
        4: "Diamond",
        5: "Isosceles Triangle",
        9: "Oval",
        12: "Cube",
        13: "Connector",
        14: "Text Box",
        # Thêm các types khác nếu cần
    }
    return shape_types.get(shape_type, f"Type_{shape_type}")

def reverse_engineer_diagram(excel_file):
    """
    Đọc và phân tích tất cả shapes trong Excel file
    
    Args:
        excel_file: Đường dẫn đến file Excel
    
    Returns:
        Dictionary chứa thông tin về tất cả shapes
    """
    
    print(f"🔍 Đang phân tích file: {excel_file}")
    
    # Mở file Excel
    wb = xw.Book(excel_file)
    
    all_sheets_info = {}
    
    # Duyệt qua tất cả các sheets
    for sheet in wb.sheets:
        print(f"\n📄 Sheet: {sheet.name}")
        
        shapes_info = []
        
        # Duyệt qua tất cả shapes trong sheet
        for i, shape in enumerate(sheet.shapes, 1):
            try:
                shape_data = {
                    "index": i,
                    "name": shape.name,
                    "type": None,
                    "type_name": None,
                    "position": {
                        "left": shape.left,
                        "top": shape.top,
                        "width": shape.width,
                        "height": shape.height
                    },
                    "text": None,
                    "font": {},
                    "fill_color": None,
                    "line_color": None,
                    "line_weight": None,
                }
                
                # Lấy shape type
                try:
                    shape_data["type"] = shape.api.Type
                    shape_data["type_name"] = get_shape_type_name(shape.api.Type)
                except:
                    pass
                
                # Lấy text content
                try:
                    if hasattr(shape.api, 'TextFrame'):
                        shape_data["text"] = shape.api.TextFrame.Characters().Text
                        
                        # Lấy font properties
                        font = shape.api.TextFrame.Characters().Font
                        shape_data["font"] = {
                            "name": font.Name if hasattr(font, 'Name') else None,
                            "size": font.Size if hasattr(font, 'Size') else None,
                            "bold": font.Bold if hasattr(font, 'Bold') else None,
                            "italic": font.Italic if hasattr(font, 'Italic') else None,
                            "color": get_rgb_from_long(font.Color) if hasattr(font, 'Color') else None,
                        }
                except:
                    pass
                
                # Lấy fill color
                try:
                    if hasattr(shape.api, 'Fill'):
                        fill_rgb = shape.api.Fill.ForeColor.RGB
                        shape_data["fill_color"] = get_rgb_from_long(fill_rgb)
                except:
                    pass
                
                # Lấy line properties
                try:
                    if hasattr(shape.api, 'Line'):
                        line = shape.api.Line
                        shape_data["line_color"] = get_rgb_from_long(line.ForeColor.RGB) if hasattr(line, 'ForeColor') else None
                        shape_data["line_weight"] = line.Weight if hasattr(line, 'Weight') else None
                        shape_data["line_style"] = line.DashStyle if hasattr(line, 'DashStyle') else None
                        
                        # Arrow head info
                        if hasattr(line, 'EndArrowheadStyle'):
                            shape_data["arrow_end"] = line.EndArrowheadStyle
                        if hasattr(line, 'BeginArrowheadStyle'):
                            shape_data["arrow_begin"] = line.BeginArrowheadStyle
                except:
                    pass
                
                # Lấy alignment
                try:
                    if hasattr(shape.api, 'TextFrame'):
                        tf = shape.api.TextFrame
                        shape_data["alignment"] = {
                            "horizontal": tf.HorizontalAlignment if hasattr(tf, 'HorizontalAlignment') else None,
                            "vertical": tf.VerticalAlignment if hasattr(tf, 'VerticalAlignment') else None,
                        }
                except:
                    pass
                
                shapes_info.append(shape_data)
                
                # In thông tin ngắn gọn
                print(f"  [{i}] {shape.name} - {shape_data['type_name']} at ({shape.left:.1f}, {shape.top:.1f})")
                if shape_data['text']:
                    print(f"      Text: {shape_data['text'][:50]}...")
                if shape_data['fill_color']:
                    print(f"      Fill: {shape_data['fill_color']}")
                    
            except Exception as e:
                print(f"  ⚠️  Lỗi khi đọc shape {i}: {e}")
        
        all_sheets_info[sheet.name] = {
            "total_shapes": len(shapes_info),
            "shapes": shapes_info
        }
    
    # Đóng workbook
    # wb.close()
    
    return all_sheets_info

def export_to_json(data, output_file):
    """Xuất thông tin shapes ra file JSON"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Đã xuất thông tin ra file: {output_file}")

def generate_recreation_code(data, output_file):
    """Tạo code Python để recreate diagram từ thông tin đã đọc"""
    
    code = '''#!/usr/bin/env python3
"""
Auto-generated code to recreate diagram
Generated by reverse_engineer_diagram.py
"""

import xlwings as xw

def recreate_diagram():
    wb = xw.Book()
    
'''
    
    for sheet_name, sheet_data in data.items():
        code += f'    # Sheet: {sheet_name}\n'
        code += f'    sheet = wb.sheets[0]\n'
        code += f'    sheet.name = "{sheet_name}"\n\n'
        
        for shape in sheet_data['shapes']:
            if shape['type_name'] in ['Rectangle', 'Diamond', 'Oval', 'Rounded Rectangle']:
                # Tạo code để vẽ shape
                code += f'    # Shape: {shape["name"]}\n'
                code += f'    shape_{shape["index"]} = sheet.shapes.api.AddShape(\n'
                code += f'        Type={shape["type"]},\n'
                code += f'        Left={shape["position"]["left"]},\n'
                code += f'        Top={shape["position"]["top"]},\n'
                code += f'        Width={shape["position"]["width"]},\n'
                code += f'        Height={shape["position"]["height"]}\n'
                code += f'    )\n'
                
                # Text
                if shape['text']:
                    code += f'    shape_{shape["index"]}.TextFrame.Characters().Text = """{shape["text"]}"""\n'
                
                # Font
                if shape['font'].get('size'):
                    code += f'    shape_{shape["index"]}.TextFrame.Characters().Font.Size = {shape["font"]["size"]}\n'
                if shape['font'].get('bold'):
                    code += f'    shape_{shape["index"]}.TextFrame.Characters().Font.Bold = True\n'
                if shape['font'].get('color'):
                    # Chuyển hex về RGB long
                    hex_color = shape['font']['color'].replace('#', '')
                    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
                    rgb_long = r + (g << 8) + (b << 16)
                    code += f'    shape_{shape["index"]}.TextFrame.Characters().Font.Color = {rgb_long}\n'
                
                # Fill color
                if shape['fill_color']:
                    hex_color = shape['fill_color'].replace('#', '')
                    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
                    rgb_long = r + (g << 8) + (b << 16)
                    code += f'    shape_{shape["index"]}.Fill.ForeColor.RGB = {rgb_long}\n'
                
                # Line
                if shape['line_weight']:
                    code += f'    shape_{shape["index"]}.Line.Weight = {shape["line_weight"]}\n'
                if shape['line_color']:
                    hex_color = shape['line_color'].replace('#', '')
                    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
                    rgb_long = r + (g << 8) + (b << 16)
                    code += f'    shape_{shape["index"]}.Line.ForeColor.RGB = {rgb_long}\n'
                
                code += '\n'
    
    code += '''    
    # Save file
    wb.save('recreated_diagram.xlsx')
    print("✅ Diagram recreated successfully!")

if __name__ == '__main__':
    recreate_diagram()
'''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(code)
    
    print(f"✅ Đã tạo recreation code: {output_file}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python reverse_engineer_diagram.py <excel_file>")
        print("\nExample:")
        print("  python reverse_engineer_diagram.py flowchart_demo.xlsx")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    
    try:
        # Reverse engineer
        diagram_info = reverse_engineer_diagram(excel_file)
        
        # Xuất ra JSON
        json_file = excel_file.replace('.xlsx', '_analysis.json')
        export_to_json(diagram_info, json_file)
        
        # Tạo recreation code
        code_file = excel_file.replace('.xlsx', '_recreate.py')
        generate_recreation_code(diagram_info, code_file)
        
        print("\n" + "="*60)
        print("📊 SUMMARY")
        print("="*60)
        for sheet_name, sheet_data in diagram_info.items():
            print(f"Sheet '{sheet_name}': {sheet_data['total_shapes']} shapes")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        print("\nLưu ý: Script này cần chạy trên Windows/Mac với Excel đã cài đặt.")