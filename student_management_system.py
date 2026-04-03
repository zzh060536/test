# 学生管理系统
# 功能：实现查询、添加、修改、删除学生信息的功能
# 数据库：SQL Server，使用Windows身份验证
# 表结构：学生表(xsb)、课程表(KC1)、成绩表(CJB)

import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
import re

# 数据库连接函数
def connect_db():
    """
    连接到SQL Server数据库
    使用Windows身份验证
    """
    try:
        # 连接字符串
        conn_str = (
            r'DRIVER={SQL Server};'
            r'SERVER=localhost\SQLEXPRESS;'
            r'DATABASE=xsgl;'
            r'Trusted_Connection=yes;'
        )
        # 建立连接
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        messagebox.showerror("错误", f"数据库连接失败: {str(e)}")
        return None

# 主应用类
class StudentManagementSystem:
    def __init__(self, root):
        """
        初始化应用
        """
        self.root = root
        self.root.title("学生管理系统")
        self.root.geometry("800x600")
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建查询区域
        self.create_search_section()
        
        # 创建结果显示区域
        self.create_result_section()
        
        # 创建功能按钮区域
        self.create_button_section()
        
        # 创建详情编辑区域
        self.create_detail_section()
        
        # 初始化数据库连接
        self.conn = connect_db()
        if self.conn:
            self.cursor = self.conn.cursor()
        else:
            self.cursor = None
    
    def create_search_section(self):
        """
        创建查询区域
        """
        search_frame = ttk.LabelFrame(self.main_frame, text="查询", padding="10")
        search_frame.pack(fill=tk.X, pady=5)
        
        # 学号查询
        ttk.Label(search_frame, text="学号:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.search_id_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_id_var, width=20).grid(row=0, column=1, padx=5, pady=5)
        
        # 姓名查询
        ttk.Label(search_frame, text="姓名:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.search_name_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_name_var, width=20).grid(row=0, column=3, padx=5, pady=5)
        
        # 查询按钮
        ttk.Button(search_frame, text="查询", command=self.search_student).grid(row=0, column=4, padx=5, pady=5)
        
        # 显示所有学生按钮
        ttk.Button(search_frame, text="显示所有", command=self.show_all_students).grid(row=0, column=5, padx=5, pady=5)
    
    def create_result_section(self):
        """
        创建结果显示区域
        """
        result_frame = ttk.LabelFrame(self.main_frame, text="查询结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建树形视图
        columns = ("学号", "姓名", "性别", "出生时间", "专业", "总学分")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # 绑定双击事件
        self.tree.bind("<Double-1>", self.on_tree_double_click)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
    
    def create_button_section(self):
        """
        创建功能按钮区域
        """
        button_frame = ttk.Frame(self.main_frame, padding="10")
        button_frame.pack(fill=tk.X, pady=5)
        
        # 添加学生按钮
        ttk.Button(button_frame, text="添加学生", command=self.add_student).pack(side=tk.LEFT, padx=5)
        
        # 修改学生按钮
        ttk.Button(button_frame, text="修改学生", command=self.update_student).pack(side=tk.LEFT, padx=5)
        
        # 删除学生按钮
        ttk.Button(button_frame, text="删除学生", command=self.delete_student).pack(side=tk.LEFT, padx=5)
        
        # 刷新按钮
        ttk.Button(button_frame, text="刷新", command=self.show_all_students).pack(side=tk.LEFT, padx=5)
    
    def create_detail_section(self):
        """
        创建详情编辑区域
        """
        detail_frame = ttk.LabelFrame(self.main_frame, text="学生详情", padding="10")
        detail_frame.pack(fill=tk.X, pady=5)
        
        # 学号
        ttk.Label(detail_frame, text="学号:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.id_var = tk.StringVar()
        ttk.Entry(detail_frame, textvariable=self.id_var, width=20).grid(row=0, column=1, padx=5, pady=5)
        
        # 姓名
        ttk.Label(detail_frame, text="姓名:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.name_var = tk.StringVar()
        ttk.Entry(detail_frame, textvariable=self.name_var, width=20).grid(row=0, column=3, padx=5, pady=5)
        
        # 性别
        ttk.Label(detail_frame, text="性别:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.gender_var = tk.StringVar(value="男")
        ttk.Radiobutton(detail_frame, text="男", variable=self.gender_var, value="男").grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Radiobutton(detail_frame, text="女", variable=self.gender_var, value="女").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        
        # 出生时间
        ttk.Label(detail_frame, text="出生时间:").grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)
        self.birth_var = tk.StringVar()
        ttk.Entry(detail_frame, textvariable=self.birth_var, width=20).grid(row=1, column=4, padx=5, pady=5)
        
        # 专业
        ttk.Label(detail_frame, text="专业:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.major_var = tk.StringVar()
        ttk.Entry(detail_frame, textvariable=self.major_var, width=20).grid(row=2, column=1, padx=5, pady=5)
        
        # 总学分
        ttk.Label(detail_frame, text="总学分:").grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)
        self.credit_var = tk.StringVar()
        ttk.Entry(detail_frame, textvariable=self.credit_var, width=20).grid(row=2, column=3, padx=5, pady=5)
        
        # 备注
        ttk.Label(detail_frame, text="备注:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.remark_var = tk.StringVar()
        ttk.Entry(detail_frame, textvariable=self.remark_var, width=40).grid(row=3, column=1, columnspan=4, padx=5, pady=5)
        
        # 课程和成绩区域
        course_frame = ttk.LabelFrame(detail_frame, text="所选课程及成绩", padding="10")
        course_frame.grid(row=4, column=0, columnspan=5, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # 课程列表
        ttk.Label(course_frame, text="课程列表:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.course_listbox = tk.Listbox(course_frame, width=30, height=5)
        self.course_listbox.grid(row=1, column=0, padx=5, pady=5)
        
        # 成绩输入
        ttk.Label(course_frame, text="成绩:").grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.score_var = tk.StringVar()
        ttk.Entry(course_frame, textvariable=self.score_var, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        # 按钮
        ttk.Button(course_frame, text="添加课程", command=self.add_course).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(course_frame, text="删除课程", command=self.remove_course).grid(row=1, column=3, padx=5, pady=5)
    
    def search_student(self):
        """
        根据学号或姓名查询学生
        """
        if not self.cursor:
            messagebox.showerror("错误", "数据库连接失败")
            return
        
        # 清空树形视图
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 获取查询条件
        student_id = self.search_id_var.get().strip()
        student_name = self.search_name_var.get().strip()
        
        # 构建SQL语句
        if student_id:
            sql = "SELECT * FROM xsb WHERE 学号 = ?"
            params = (student_id,)
        elif student_name:
            sql = "SELECT * FROM xsb WHERE 姓名 LIKE ?"
            params = (f"%{student_name}%",)
        else:
            messagebox.showinfo("提示", "请输入查询条件")
            return
        
        try:
            # 执行查询
            self.cursor.execute(sql, params)
            rows = self.cursor.fetchall()
            
            # 显示结果
            for row in rows:
                # 处理性别显示
                gender = "男" if row.性别 else "女"
                # 插入数据到树形视图
                self.tree.insert("", tk.END, values=(
                    row.学号, row.姓名, gender, row.出生时间, row.专业, row.总学分
                ))
        except Exception as e:
            messagebox.showerror("错误", f"查询失败: {str(e)}")
    
    def show_all_students(self):
        """
        显示所有学生信息
        """
        if not self.cursor:
            messagebox.showerror("错误", "数据库连接失败")
            return
        
        # 清空树形视图
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 构建SQL语句
        sql = "SELECT * FROM xsb"
        
        try:
            # 执行查询
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            
            # 显示结果
            for row in rows:
                # 处理性别显示
                gender = "男" if row.性别 else "女"
                # 插入数据到树形视图
                self.tree.insert("", tk.END, values=(
                    row.学号, row.姓名, gender, row.出生时间, row.专业, row.总学分
                ))
        except Exception as e:
            messagebox.showerror("错误", f"查询失败: {str(e)}")
    
    def on_tree_double_click(self, event):
        """
        双击树形视图项时，显示详情
        """
        # 获取选中的项
        item = self.tree.selection()[0]
        # 获取项的值
        values = self.tree.item(item, "values")
        
        # 填充详情区域
        self.id_var.set(values[0])
        self.name_var.set(values[1])
        self.gender_var.set(values[2])
        self.birth_var.set(values[3])
        self.major_var.set(values[4])
        self.credit_var.set(values[5])
        
        # 加载学生的课程和成绩
        self.load_student_courses(values[0])
        
        # 加载备注
        if self.cursor:
            try:
                sql = "SELECT 备注 FROM xsb WHERE 学号 = ?"
                self.cursor.execute(sql, (values[0],))
                row = self.cursor.fetchone()
                if row:
                    self.remark_var.set(row.备注 or "")
            except Exception as e:
                messagebox.showerror("错误", f"加载备注失败: {str(e)}")
    
    def load_student_courses(self, student_id):
        """
        加载学生的课程和成绩
        """
        if not self.cursor:
            return
        
        # 清空课程列表
        self.course_listbox.delete(0, tk.END)
        
        # 构建SQL语句
        sql = """
        SELECT KC1.课程号, KC1.课程名, CJB.成绩
        FROM CJB
        JOIN KC1 ON CJB.课程号 = KC1.课程号
        WHERE CJB.学号 = ?
        """
        
        try:
            # 执行查询
            self.cursor.execute(sql, (student_id,))
            rows = self.cursor.fetchall()
            
            # 显示课程和成绩
            for row in rows:
                self.course_listbox.insert(tk.END, f"{row.课程号} - {row.课程名}: {row.成绩}")
        except Exception as e:
            messagebox.showerror("错误", f"加载课程失败: {str(e)}")
    
    def add_student(self):
        """
        添加学生
        """
        if not self.cursor:
            messagebox.showerror("错误", "数据库连接失败")
            return
        
        # 获取学生信息
        student_id = self.id_var.get().strip()
        student_name = self.name_var.get().strip()
        gender = 1 if self.gender_var.get() == "男" else 0
        birth_date = self.birth_var.get().strip()
        major = self.major_var.get().strip()
        credit = self.credit_var.get().strip()
        remark = self.remark_var.get().strip()
        
        # 验证输入
        if not student_id or not student_name:
            messagebox.showinfo("提示", "学号和姓名不能为空")
            return
        
        # 验证学号格式
        if not re.match(r'^\d{6}$', student_id):
            messagebox.showinfo("提示", "学号格式不正确，应为6位数字")
            return
        
        # 验证出生日期格式
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', birth_date):
            messagebox.showinfo("提示", "出生日期格式不正确，应为YYYY-MM-DD")
            return
        
        # 验证总学分
        if credit and not credit.isdigit():
            messagebox.showinfo("提示", "总学分应为数字")
            return
        
        credit = int(credit) if credit else 0
        
        try:
            # 检查学号是否已存在
            self.cursor.execute("SELECT * FROM xsb WHERE 学号 = ?", (student_id,))
            if self.cursor.fetchone():
                messagebox.showinfo("提示", "学号已存在")
                return
            
            # 插入学生信息
            sql = """
            INSERT INTO xsb (学号, 姓名, 性别, 出生时间, 专业, 总学分, 备注)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            self.cursor.execute(sql, (student_id, student_name, gender, birth_date, major, credit, remark))
            self.conn.commit()
            
            messagebox.showinfo("成功", "学生添加成功")
            # 刷新学生列表
            self.show_all_students()
            # 清空输入
            self.clear_inputs()
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("错误", f"添加学生失败: {str(e)}")
    
    def update_student(self):
        """
        修改学生信息
        """
        if not self.cursor:
            messagebox.showerror("错误", "数据库连接失败")
            return
        
        # 获取学生信息
        student_id = self.id_var.get().strip()
        student_name = self.name_var.get().strip()
        gender = 1 if self.gender_var.get() == "男" else 0
        birth_date = self.birth_var.get().strip()
        major = self.major_var.get().strip()
        credit = self.credit_var.get().strip()
        remark = self.remark_var.get().strip()
        
        # 验证输入
        if not student_id:
            messagebox.showinfo("提示", "请选择要修改的学生")
            return
        
        # 验证出生日期格式
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', birth_date):
            messagebox.showinfo("提示", "出生日期格式不正确，应为YYYY-MM-DD")
            return
        
        # 验证总学分
        if credit and not credit.isdigit():
            messagebox.showinfo("提示", "总学分应为数字")
            return
        
        credit = int(credit) if credit else 0
        
        try:
            # 检查学号是否存在
            self.cursor.execute("SELECT * FROM xsb WHERE 学号 = ?", (student_id,))
            if not self.cursor.fetchone():
                messagebox.showinfo("提示", "学号不存在")
                return
            
            # 更新学生信息
            sql = """
            UPDATE xsb
            SET 姓名 = ?, 性别 = ?, 出生时间 = ?, 专业 = ?, 总学分 = ?, 备注 = ?
            WHERE 学号 = ?
            """
            self.cursor.execute(sql, (student_name, gender, birth_date, major, credit, remark, student_id))
            self.conn.commit()
            
            messagebox.showinfo("成功", "学生信息修改成功")
            # 刷新学生列表
            self.show_all_students()
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("错误", f"修改学生信息失败: {str(e)}")
    
    def delete_student(self):
        """
        删除学生
        """
        if not self.cursor:
            messagebox.showerror("错误", "数据库连接失败")
            return
        
        # 获取选中的学生
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("提示", "请选择要删除的学生")
            return
        
        # 确认删除
        if not messagebox.askyesno("确认", "确定要删除选中的学生吗？"):
            return
        
        try:
            # 删除学生的成绩记录
            for item in selected_items:
                student_id = self.tree.item(item, "values")[0]
                # 删除成绩记录
                self.cursor.execute("DELETE FROM CJB WHERE 学号 = ?", (student_id,))
                # 删除学生记录
                self.cursor.execute("DELETE FROM xsb WHERE 学号 = ?", (student_id,))
            
            self.conn.commit()
            messagebox.showinfo("成功", "学生删除成功")
            # 刷新学生列表
            self.show_all_students()
            # 清空输入
            self.clear_inputs()
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("错误", f"删除学生失败: {str(e)}")
    
    def add_course(self):
        """
        添加课程和成绩
        """
        if not self.cursor:
            messagebox.showerror("错误", "数据库连接失败")
            return
        
        # 获取学生学号
        student_id = self.id_var.get().strip()
        if not student_id:
            messagebox.showinfo("提示", "请选择学生")
            return
        
        # 获取课程号和成绩
        course_info = self.score_var.get().strip().split()
        if len(course_info) != 2:
            messagebox.showinfo("提示", "请输入课程号和成绩，格式：课程号 成绩")
            return
        
        course_id, score = course_info
        
        # 验证课程号格式
        if not re.match(r'^\d{3}$', course_id):
            messagebox.showinfo("提示", "课程号格式不正确，应为3位数字")
            return
        
        # 验证成绩
        if not score.isdigit() or not (0 <= int(score) <= 100):
            messagebox.showinfo("提示", "成绩应为0-100之间的数字")
            return
        
        score = int(score)
        
        try:
            # 检查课程是否存在
            self.cursor.execute("SELECT * FROM KC1 WHERE 课程号 = ?", (course_id,))
            if not self.cursor.fetchone():
                messagebox.showinfo("提示", "课程号不存在")
                return
            
            # 检查是否已选该课程
            self.cursor.execute("SELECT * FROM CJB WHERE 学号 = ? AND 课程号 = ?", (student_id, course_id))
            if self.cursor.fetchone():
                messagebox.showinfo("提示", "该学生已选此课程")
                return
            
            # 添加课程和成绩
            self.cursor.execute("INSERT INTO CJB (学号, 课程号, 成绩) VALUES (?, ?, ?)", (student_id, course_id, score))
            self.conn.commit()
            
            # 刷新课程列表
            self.load_student_courses(student_id)
            # 清空成绩输入
            self.score_var.set("")
            
            messagebox.showinfo("成功", "课程添加成功")
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("错误", f"添加课程失败: {str(e)}")
    
    def remove_course(self):
        """
        删除课程
        """
        if not self.cursor:
            messagebox.showerror("错误", "数据库连接失败")
            return
        
        # 获取学生学号
        student_id = self.id_var.get().strip()
        if not student_id:
            messagebox.showinfo("提示", "请选择学生")
            return
        
        # 获取选中的课程
        selected_index = self.course_listbox.curselection()
        if not selected_index:
            messagebox.showinfo("提示", "请选择要删除的课程")
            return
        
        # 提取课程号
        course_info = self.course_listbox.get(selected_index[0])
        course_id = course_info.split()[0]
        
        try:
            # 删除课程
            self.cursor.execute("DELETE FROM CJB WHERE 学号 = ? AND 课程号 = ?", (student_id, course_id))
            self.conn.commit()
            
            # 刷新课程列表
            self.load_student_courses(student_id)
            
            messagebox.showinfo("成功", "课程删除成功")
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("错误", f"删除课程失败: {str(e)}")
    
    def clear_inputs(self):
        """
        清空输入
        """
        self.id_var.set("")
        self.name_var.set("")
        self.gender_var.set("男")
        self.birth_var.set("")
        self.major_var.set("")
        self.credit_var.set("")
        self.remark_var.set("")
        self.score_var.set("")
        self.course_listbox.delete(0, tk.END)

# 主函数
if __name__ == "__main__":
    # 创建主窗口
    root = tk.Tk()
    # 创建应用实例
    app = StudentManagementSystem(root)
    # 显示所有学生
    app.show_all_students()
    # 运行主循环
    root.mainloop()
