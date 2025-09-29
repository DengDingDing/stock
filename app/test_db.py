import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

# 使用相对路径导入，因为这是作为模块运行的
from .database import AsyncSessionLocal, async_engine, Base
from . import crud

async def main():
    """为数据库读写操作量身定做的异步测试函数。"""
    print("--- 开始异步数据库读写测试 ---")

    # 1. 异步方式创建所有表
    print("正在初始化数据库和表...")
    async with async_engine.begin() as conn:
        # 使用 run_sync 来执行同步的 create_all 方法
        await conn.run_sync(Base.metadata.create_all)
    print("数据库表初始化完成。")

    # 2. 获取一个异步数据库会话
    async with AsyncSessionLocal() as db:
        # 3. 定义测试数据
        test_symbol = "TEST"
        print(f"将要获取或创建股票信息: symbol={test_symbol}")

        # 4. 调用异步的CRUD函数
        # get_or_create_stock_info 函数本身就包含了读和写两种操作
        stock_info = await crud.get_or_create_stock_info(db, symbol=test_symbol)

        # 5. 验证结果
        if stock_info and stock_info.symbol == test_symbol:
            print("读取/创建成功！")
            print(f"  - ID: {stock_info.id}")
            print(f"  - Symbol: {stock_info.symbol}")
            print(f"  - Company Name: {stock_info.company_name}")
            print(">>> 验证通过：成功从数据库获取或创建了记录。")
        else:
            print(">>> 验证失败：未能获取或创建记录。")

    print("--- 测试结束，数据库会话已自动关闭 ---")


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())