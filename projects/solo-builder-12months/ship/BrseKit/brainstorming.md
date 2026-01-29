Tôi muốn brainstorming cho một hệ thống Project AI assistant để giải quyết các paintpoint sau.
BrSE :

- phải ôm đồm quá nhiều việc từ quản lý (vì BrSE thường kiêm luôn PM), giao tiếp / nego với khách hàng, đọc kết quả research / kết quả làm việc của team offshore và định hướng.
  Tester :
- Chỉ biết về nghiệp vụ mà không hiểu về kỹ thuật
  BA :
- Có những dự án không có BA, và BrSE phải kiêm luôn BA trong khi skill BA yếu
- Có BA thì họ cũng chỉ chăm chăm vào tính năng mà không hiểu khách hàng muốn gì, hay business của khách hàng là gì..
  PM :
- ## Nhiều PM chỉ hiểu hời hợi về tech, và quản lý schedule kém, cũng không làm ra được cái report weekly cho ra hồn.
  Tôi hình dùng hệ thống Project AI Assistant (gọi là PAA) sẽ có những đặc điểm sau :

## Tư tưởng :

- Làm hết những việc nhàm chán mà AI làm tốt : tạo tài liệu (SRS, test case.. ) , fetch data, reserach
- Để cho BrSE và các thành viên khác làm những việc có giá trị cao hơn như là suy nghĩ về business của khách hàng, giao tiếp với khách hàng, tìm kiếm thêm cơ hội công việc..

## Công cụ

- Làm tài liệu xlsx, pptx tốt
- Transcript video họp với khách hàng để tổng hợp nội dung, phân tích tính cách, tâm lý và thậm chí là xu hướng giao tiếp tiếng Nhật của khách
- Quản lý memory tập trung, để cả team có chung một nguồn thông tin
- Làm việc mượt mà với Slack, Backlog , Jira, Google workspace, Teams..

## Kỳ vọng cải thiện hiệu suất :

- Với PAA thì chỉ cần 1 BrSe và 1 offshore (dev) có thể làm việc hiệu quả bằng 6 người ở mô hình cũ. 1BrSE, 1 PM, 3 dev, 1 tester

## Bản chất công nghệ :

- Dùng như một clawdbot hoặc là một lớp wrapper bên ngoài claude code. Tận dụng khả năng mạnh mẽ của claude code, là lớp core trung tâm.
- Ứng dụng hooks để validate, đặt lớp security
- Chạy trong docker containter, luôn chạy trên bản sao của dữ liệu thật, không có quyền xóa..
