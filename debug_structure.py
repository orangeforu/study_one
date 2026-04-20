#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试脚本 - 分析 book118 文档页面结构
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def analyze_page_structure():
    """分析页面结构"""
    edge_options = Options()
    edge_options.add_argument("--window-size=1920,1080")
    edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])

    driver = webdriver.Edge(options=edge_options)
    wait = WebDriverWait(driver, 15)

    try:
        # 打开一个免费文档
        test_url = "https://max.book118.com/html/2022/1214/8042135133005021.shtm"
        print(f"打开文档：{test_url}")
        driver.get(test_url)
        time.sleep(5)

        print("\n" + "="*60)
        print("页面结构分析")
        print("="*60)

        # 1. 获取页面标题
        print(f"\n页面标题：{driver.title}")

        # 2. 查找所有可能的文档容器
        print("\n--- 查找文档容器 ---")
        selectors = [
            "#doc-viewer",
            ".doc-container",
            ".document-box",
            ".doc-content",
            ".reader-container",
            ".main-content",
            "[class*='doc-viewer']",
            "[class*='document-viewer']",
            ".content-wrap",
            "#pageContainer",
            ".page-container"
        ]

        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for elem in elements:
                        if elem.is_displayed():
                            rect = elem.rect
                            print(f"✓ {selector}")
                            print(f"  位置：x={rect['x']}, y={rect['y']}, w={rect['width']}, h={rect['height']}")
            except Exception as e:
                pass

        # 3. 查找 canvas 或 img 元素（文档内容）
        print("\n--- 查找文档内容元素 (canvas/img) ---")
        content_elements = driver.find_elements(By.CSS_SELECTOR, "canvas, img[src*='page'], .doc-page-img")
        print(f"找到 {len(content_elements)} 个元素")
        for i, elem in enumerate(content_elements[:5]):
            try:
                rect = elem.rect
                src = elem.get_attribute("src")[:50] if elem.tag_name == "img" else "canvas"
                print(f"  [{i}] {elem.tag_name}: x={rect['x']}, y={rect['y']}, w={rect['width']}, h={rect['height']}, src={src}")
            except Exception as e:
                print(f"  [{i}] 错误：{e}")

        # 4. 查找翻页按钮
        print("\n--- 查找翻页按钮 ---")
        next_selectors = [
            "a[owa-btn='had']",
            "a.next[title='下一页']",
            ".btn-next",
            ".next-btn"
        ]
        for selector in next_selectors:
            try:
                elems = driver.find_elements(By.CSS_SELECTOR, selector)
                if elems and elems[0].is_displayed():
                    rect = elems[0].rect
                    print(f"✓ {selector}: x={rect['x']}, y={rect['y']}")
            except:
                pass

        # 5. 查找页码显示
        print("\n--- 查找页码显示 ---")
        page_selectors = [
            ".page-info",
            ".page-total",
            ".total-page",
            ".page-sel",
            "[class*='page'][class*='info']"
        ]
        for selector in page_selectors:
            try:
                elems = driver.find_elements(By.CSS_SELECTOR, selector)
                if elems:
                    text = elems[0].text.strip()
                    if text:
                        print(f"✓ {selector}: '{text}'")
            except:
                pass

        # 6. 获取页面完整 HTML 结构（简化的）
        print("\n--- 页面 HTML 结构（前 3 层）---")
        try:
            html = driver.find_element(By.TAG_NAME, "body")
            children = html.find_elements(By.XPATH, "./*")
            print(f"body 下有 {len(children)} 个直接子元素")
            for child in children[:10]:
                tag = child.tag_name
                class_name = child.get_attribute("class") or ""
                id_name = child.get_attribute("id") or ""
                print(f"  <{tag} id='{id_name}' class='{class_name[:50]}'>")
        except Exception as e:
            print(f"错误：{e}")

        # 7. 保存页面截图
        screenshot_path = "debug_page_structure.png"
        driver.save_screenshot(screenshot_path)
        print(f"\n页面截图已保存：{screenshot_path}")

        print("\n" + "="*60)
        print("按 Enter 键继续查看当前文档内容区域...")
        input()

        # 8. 滚动到文档区域
        print("\n尝试定位文档主内容区...")
        try:
            # 查找 iframe（很多文档网站使用 iframe 显示文档）
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            print(f"找到 {len(iframes)} 个 iframe")
            for i, iframe in enumerate(iframes):
                try:
                    rect = iframe.rect
                    src = iframe.get_attribute("src")[:50]
                    print(f"  [{i}] iframe: x={rect['x']}, y={rect['y']}, w={rect['width']}, h={rect['height']}, src={src}")
                except Exception as e:
                    print(f"  [{i}] 错误：{e}")
        except Exception as e:
            print(f"错误：{e}")

        print("\n" + "="*60)
        print("分析完成！")
        print("页面截图：debug_page_structure.png")
        print("="*60)

    except Exception as e:
        print(f"错误：{e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    analyze_page_structure()
