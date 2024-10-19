from app import create_app, db
from app.models import User

# 创建Flask应用
app = create_app()

# 启动应用
if __name__ == '__main__':
    # 启动Flask调试模式
    app.run(debug=True)
