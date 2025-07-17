from chatdoc_api import upload_txt_file, split_file, embed_file

file_id = upload_txt_file("uploaded_docs/AnHuiUniversity.txt", "AnHuiUniversity.txt")
split_file(file_id)
embed_file(file_id)

print(file_id)  # 打印最终的 file_id，复制下来