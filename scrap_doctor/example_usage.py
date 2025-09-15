#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医生爬虫使用示例
展示如何使用爬虫脚本的各种功能
"""

from doctor_scraper_v2 import DoctorScraperV2
import json

def example_basic_usage():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    # 创建爬虫实例
    scraper = DoctorScraperV2()
    
    # 爬取妇产科医生（默认配置）
    doctors = scraper.scrape_doctors(
        search_keyword="妇产科",
        max_pages=1,      # 只爬取1页
        page_size=5       # 每页5个医生
    )
    
    if doctors:
        print(f"成功获取 {len(doctors)} 位医生")
        scraper.save_results(doctors, "妇产科医生.json")
    else:
        print("没有获取到医生数据")

def example_custom_search():
    """自定义搜索示例"""
    print("\n=== 自定义搜索示例 ===")
    
    scraper = DoctorScraperV2()
    
    # 搜索不同科室的医生
    departments = ["内科", "外科", "儿科"]
    
    for dept in departments:
        print(f"\n正在搜索 {dept} 科室的医生...")
        
        doctors = scraper.scrape_doctors(
            search_keyword=dept,
            max_pages=1,
            page_size=3
        )
        
        if doctors:
            filename = f"{dept}医生.json"
            scraper.save_results(doctors, filename)
            print(f"{dept}科室：获取到 {len(doctors)} 位医生，已保存到 {filename}")
        else:
            print(f"{dept}科室：没有获取到医生数据")

def example_single_doctor():
    """单个医生信息获取示例"""
    print("\n=== 单个医生信息获取示例 ===")
    
    scraper = DoctorScraperV2()
    
    # 获取医生列表
    doctors = scraper.get_doctor_list("妇产科", page=1, page_size=1)
    
    if doctors:
        doctor = doctors[0]
        print(f"医生姓名：{doctor['name']}")
        print(f"医生级别：{doctor['level']}")
        print(f"所属医院：{doctor['hospital']}")
        print(f"所属科室：{doctor['department']}")
        
        # 构建健康页面URL
        health_url = scraper.build_doctor_home_url(doctor['doc_id'])
        print(f"健康页面URL：{health_url}")
        
        # 获取个人主页URL
        if doctor.get('expert_id'):
            author_url = scraper.get_doctor_author_home(doctor['doc_id'], doctor['expert_id'])
            print(f"个人主页URL：{author_url}")
    else:
        print("没有获取到医生数据")

def example_batch_processing():
    """批量处理示例"""
    print("\n=== 批量处理示例 ===")
    
    scraper = DoctorScraperV2()
    
    # 批量搜索多个科室
    departments = ["妇产科", "内科", "外科"]
    all_results = {}
    
    for dept in departments:
        print(f"\n处理 {dept} 科室...")
        
        doctors = scraper.scrape_doctors(
            search_keyword=dept,
            max_pages=1,
            page_size=5
        )
        
        all_results[dept] = doctors
        print(f"{dept}科室：{len(doctors)} 位医生")
    
    # 保存所有结果
    scraper.save_results(all_results, "所有科室医生.json")
    print(f"\n所有结果已保存，共 {len(all_results)} 个科室")
    
    # 打印统计信息
    scraper.print_statistics()

def example_error_handling():
    """错误处理示例"""
    print("\n=== 错误处理示例 ===")
    
    try:
        scraper = DoctorScraperV2()
        
        # 尝试搜索不存在的科室
        doctors = scraper.scrape_doctors(
            search_keyword="不存在的科室",
            max_pages=1,
            page_size=5
        )
        
        if doctors:
            print(f"意外获取到 {len(doctors)} 位医生")
        else:
            print("如预期，没有获取到医生数据")
            
    except Exception as e:
        print(f"发生错误：{e}")
        print("错误处理正常工作")

def main():
    """主函数"""
    print("医生爬虫使用示例")
    print("="*50)
    
    try:
        # 运行各种示例
        example_basic_usage()
        example_custom_search()
        example_single_doctor()
        example_batch_processing()
        example_error_handling()
        
    except KeyboardInterrupt:
        print("\n用户中断程序")
    except Exception as e:
        print(f"\n程序运行出错：{e}")
    
    print("\n所有示例运行完成！")


if __name__ == "__main__":
    main()
