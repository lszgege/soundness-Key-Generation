import pexpect
import os
import shutil


def check_soundness_cli():
    return shutil.which("soundness-cli") is not None


def run_soundness_generate_key(name, password, output_file):
    try:
        command = f"soundness-cli generate-key --name {name}"
        child = pexpect.spawn(command, encoding='utf-8', timeout=30)

        # 用于累积完整输出
        full_output = ""

        # 等待第一个密码提示
        index = child.expect([
            "Enter password for secret key:",
            "Error: Key pair with name",
            pexpect.EOF
        ])
        full_output += child.before  # 捕获助记词等前期输出

        if index == 0:
            child.sendline(password)
            full_output += "Enter password for secret key:\n" + password + "\n"

            # 等待确认密码提示
            child.expect("Confirm password:")
            full_output += child.before
            child.sendline(password)
            full_output += "Confirm password:\n" + password + "\n"

            # 等待命令结束
            child.expect(pexpect.EOF)
            full_output += child.before
        elif index == 1:
            print(f"{name} 已存在，跳过")
            return False
        else:
            print(f"执行 {name} 时发生未知错误")
            return False

        # 调试：打印完整输出
        print(f"DEBUG: 完整输出:\n{full_output}\n---END---")

        if "✅ Generated new key pair" not in full_output:
            print(f"生成 {name} 失败: {full_output}")
            return False

        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(f"--- {name} ---\n{full_output}\n\n")

        print(f"已生成 {name} 并记录到 {output_file}")
        return True

    except pexpect.ExceptionPexpect as e:
        print(f"执行 {name} 时发生错误: {str(e)}")
        return False


if __name__ == "__main__":
    if not check_soundness_cli():
        print("错误: soundness-cli 未安装或不在当前目录/PATH 中，请确保环境正确！")
        exit(1)

    folder_path = os.getcwd()
    output_file = os.path.join(folder_path, "key_records.txt")
    password = "password"
    # 这里输入你要的秘钥数量 
    num_keys = 5

    try:
        with open(output_file, 'a') as f:
            pass
    except PermissionError:
        print(f"错误: 没有权限在当前目录 {folder_path} 中写入文件")
        exit(1)
    except Exception as e:
        print(f"创建文件时出错: {str(e)}")
        exit(1)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Soundness CLI Key Generation Output\n\n")

    try:
        for i in range(1, num_keys + 1):
            # 修改秘钥名称，秘钥名称是不能重复的
            name = f"SpringDAO{i}"
            success = run_soundness_generate_key(name, password, output_file)

            if success:
                print(f"进度: {i}/{num_keys} 成功生成 {name}")
            else:
                print(f"进度: {i}/{num_keys} 生成 {name} 失败或跳过")
    except KeyboardInterrupt:
        print("\n用户中断程序，退出...")
        exit(0)
    except Exception as e:
        print(f"程序异常终止: {str(e)}")
        exit(1)

    print(f"完成！共尝试生成 {num_keys} 个密钥对，结果保存在 {output_file}")
