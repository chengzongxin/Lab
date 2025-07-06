// 调试工具 - 用于诊断插件问题
class DebugTool {
    constructor() {
        this.init();
    }

    init() {
        console.log('🔧 调试工具已加载');
        this.addDebugCommands();
    }

    // 添加调试命令到控制台
    addDebugCommands() {
        // 测试页面元素
        window.testPageElements = () => {
            console.log('🔍 测试页面元素...');
            
            const results = {
                tableRows: document.querySelectorAll('tr[data-testid="beast-core-table-body-tr"]').length,
                checkboxes: document.querySelectorAll('input[type="checkbox"]').length,
                productTitles: document.querySelectorAll('.goods-info_title__yHBeG').length,
                priceElements: document.querySelectorAll('td:nth-child(5) span span:last-child').length
            };
            
            console.log('页面元素统计:', results);
            
            // 测试第一个商品信息
            const firstRow = document.querySelector('tr[data-testid="beast-core-table-body-tr"]');
            if (firstRow) {
                const title = firstRow.querySelector('.goods-info_title__yHBeG');
                const price = firstRow.querySelector('td:nth-child(5) span span:last-child');
                const checkbox = firstRow.querySelector('input[type="checkbox"]');
                
                console.log('第一个商品信息:', {
                    title: title ? title.textContent.trim() : '未找到',
                    price: price ? price.textContent.trim() : '未找到',
                    checkbox: checkbox ? (checkbox.checked ? '已勾选' : '未勾选') : '未找到'
                });
                
                // 详细检查第一个商品
                if (title) {
                    console.log('商品名称元素详情:', {
                        textContent: title.textContent,
                        innerHTML: title.innerHTML.substring(0, 200) + '...',
                        className: title.className
                    });
                }
                
                if (price) {
                    console.log('价格元素详情:', {
                        textContent: price.textContent,
                        innerHTML: price.innerHTML,
                        className: price.className
                    });
                }
            }
            
            return results;
        };

        // 测试插件状态
        window.testPluginStatus = () => {
            console.log('🔧 测试插件状态...');
            
            if (window.autoCheckManager) {
                console.log('插件管理器状态:', {
                    isRunning: window.autoCheckManager.isRunning,
                    categories: window.autoCheckManager.categories,
                    processedRows: window.autoCheckManager.processedRows.size
                });
                
                const stats = window.autoCheckManager.getPageStats();
                console.log('页面统计:', stats);
            } else {
                console.log('❌ 插件管理器未找到');
            }
        };

        // 手动触发检查
        window.manualCheck = () => {
            console.log('🔍 手动触发检查...');
            
            if (window.autoCheckManager) {
                window.autoCheckManager.checkCurrentRows();
            } else {
                console.log('❌ 插件管理器未找到');
            }
        };

        // 测试勾选功能
        window.testCheckbox = (rowIndex = 0) => {
            console.log('🔍 测试勾选功能...');
            
            const rows = document.querySelectorAll('tr[data-testid="beast-core-table-body-tr"]');
            if (rows.length === 0) {
                console.log('❌ 未找到表格行');
                return;
            }
            
            const row = rows[rowIndex];
            if (!row) {
                console.log(`❌ 未找到第${rowIndex}行`);
                return;
            }
            
            console.log('测试行:', row);
            
            // 查找自定义checkbox的label
            const label = row.querySelector('label[data-testid="beast-core-checkbox"]');
            if (!label) {
                console.log('❌ 未找到checkbox label');
                return;
            }
            
            console.log('找到checkbox label:', label);
            console.log('当前data-checked状态:', label.getAttribute('data-checked'));
            console.log('当前CSS类:', label.className);
            
            // 查找相关元素
            const input = label.querySelector('input[type="checkbox"]');
            const square = label.querySelector('.CBX_square_5-118-0');
            const icon = label.querySelector('.CBX_iconCheck_5-118-0');
            
            console.log('相关元素状态:', {
                input: input ? input.checked : 'N/A',
                squareClasses: square ? square.className : 'N/A',
                iconClasses: icon ? icon.className : 'N/A'
            });
            
            // 尝试勾选
            if (label.getAttribute('data-checked') !== 'true') {
                console.log('🔧 开始勾选操作...');
                
                // 使用新的勾选逻辑
                if (window.autoCheckManager && window.autoCheckManager.checkRow) {
                    window.autoCheckManager.checkRow(row);
                } else {
                    // 手动执行勾选逻辑
                    label.setAttribute('data-checked', 'true');
                    label.setAttribute('data-indeterminate', 'false');
                    label.classList.add('CBX_active_5-118-0');
                    
                    if (input) {
                        input.checked = true;
                        input.indeterminate = false;
                    }
                    
                    if (square) {
                        square.classList.add('CBX_active_5-118-0');
                    }
                    
                    if (icon) {
                        icon.classList.add('CBX_active_5-118-0');
                    }
                    
                    label.click();
                }
                
                console.log('✅ 勾选操作完成');
                console.log('勾选后状态:', {
                    dataChecked: label.getAttribute('data-checked'),
                    hasActiveClass: label.classList.contains('CBX_active_5-118-0'),
                    inputChecked: input ? input.checked : 'N/A'
                });
            } else {
                console.log('ℹ️ 该行已经勾选');
            }
            
            return { label, input, square, icon };
        };

        // 测试品类匹配
        window.testCategoryMatch = (productName, keyword) => {
            console.log('🔍 测试品类匹配...');
            
            if (window.autoCheckManager) {
                const result = window.autoCheckManager.matchesCategory(productName, keyword);
                console.log(`匹配结果: "${productName}" 匹配 "${keyword}" = ${result}`);
                return result;
            } else {
                console.log('❌ 插件管理器未找到');
                return false;
            }
        };

        // 测试第一行商品的匹配
        window.testFirstRow = () => {
            console.log('🔍 测试第一行商品匹配...');
            
            const firstRow = document.querySelector('tr[data-testid="beast-core-table-body-tr"]');
            if (!firstRow) {
                console.log('❌ 未找到表格行');
                return;
            }
            
            if (window.autoCheckManager) {
                const shouldCheck = window.autoCheckManager.shouldCheckRow(firstRow);
                console.log('第一行是否应该勾选:', shouldCheck);
                return shouldCheck;
            } else {
                console.log('❌ 插件管理器未找到');
                return false;
            }
        };

        // 测试所有配置的品类
        window.testAllCategories = () => {
            console.log('🔍 测试所有品类配置...');
            
            if (window.autoCheckManager && window.autoCheckManager.categories) {
                console.log('当前配置的品类:', window.autoCheckManager.categories);
                
                const firstRow = document.querySelector('tr[data-testid="beast-core-table-body-tr"]');
                if (firstRow) {
                    const titleElement = firstRow.querySelector('.goods-info_title__yHBeG');
                    if (titleElement) {
                        const productName = titleElement.textContent.trim().replace(/\{[^}]*\}/g, '').trim();
                        console.log('第一行商品名称:', productName);
                        
                        window.autoCheckManager.categories.forEach((category, index) => {
                            const isMatch = window.autoCheckManager.matchesCategory(productName, category.keyword);
                            console.log(`品类 ${index + 1}: "${category.keyword}" -> 匹配 = ${isMatch}`);
                        });
                    }
                }
            } else {
                console.log('❌ 插件管理器或品类配置未找到');
            }
        };

        // 测试滚动功能
        window.testScroll = () => {
            console.log('📜 测试滚动功能...');
            
            if (window.autoCheckManager && window.autoCheckManager.scrollToBottom) {
                window.autoCheckManager.scrollToBottom();
                console.log('✅ 滚动命令已执行');
            } else {
                console.log('❌ 滚动功能未找到');
            }
        };

        // 手动触发滚动检查
        window.triggerScrollCheck = () => {
            console.log('🔄 手动触发滚动检查...');
            
            if (window.autoCheckManager && window.autoCheckManager.checkAndScroll) {
                window.autoCheckManager.checkAndScroll();
                console.log('✅ 滚动检查已触发');
            } else {
                console.log('❌ 滚动检查功能未找到');
            }
        };

        // 检查页面滚动容器
        window.checkScrollContainers = () => {
            console.log('🔍 检查页面滚动容器...');
            
            // 检查页面滚动信息
            const pageInfo = {
                documentHeight: document.body.scrollHeight,
                windowHeight: window.innerHeight,
                currentScrollTop: window.pageYOffset || document.documentElement.scrollTop,
                maxScrollTop: document.body.scrollHeight - window.innerHeight
            };
            console.log('页面滚动信息:', pageInfo);
            
            // 查找所有可能的滚动容器
            const selectors = [
                '[style*="overflow"]',
                '[class*="scroll"]',
                '[class*="table"]',
                '.ant-table-body',
                '.el-table__body-wrapper',
                '.table-container',
                '.scroll-container'
            ];
            
            selectors.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                console.log(`选择器 "${selector}" 找到 ${elements.length} 个元素`);
                
                elements.forEach((element, index) => {
                    const style = window.getComputedStyle(element);
                    const scrollInfo = {
                        element: element,
                        className: element.className,
                        scrollHeight: element.scrollHeight,
                        clientHeight: element.clientHeight,
                        overflow: style.overflow,
                        overflowY: style.overflowY,
                        canScroll: element.scrollHeight > element.clientHeight
                    };
                    console.log(`元素 ${index}:`, scrollInfo);
                });
            });
            
            // 查找表格容器
            if (window.autoCheckManager && window.autoCheckManager.findTableContainer) {
                const tableContainer = window.autoCheckManager.findTableContainer();
                console.log('找到的表格容器:', tableContainer);
            }
        };

        // 显示帮助信息
        window.debugHelp = () => {
            console.log(`
🔧 调试命令帮助:

1. testPageElements() - 测试页面元素是否存在
2. testPluginStatus() - 检查插件状态
3. manualCheck() - 手动触发商品检查
4. testCheckbox(rowIndex) - 测试勾选功能（rowIndex默认为0）
5. testCustomCheckbox() - 测试自定义checkbox组件
6. testForceCheck(rowIndex) - 测试强制勾选（rowIndex默认为0）
7. testActiveClass(rowIndex) - 测试CSS类添加（rowIndex默认为0）
8. testSupplementCheck(rowIndex) - 测试补充勾选（rowIndex默认为0）
9. testCategoryMatch(productName, keyword) - 测试品类匹配
10. testFirstRow() - 测试第一行商品匹配
11. testAllCategories() - 测试所有品类配置
12. testScroll() - 测试滚动功能
13. triggerScrollCheck() - 手动触发滚动检查
14. checkScrollContainers() - 检查页面滚动容器
15. debugHelp() - 显示此帮助信息

示例用法:
- testPageElements()  // 检查页面元素
- testFirstRow()  // 测试第一行匹配
- testAllCategories()  // 测试所有品类
- checkScrollContainers()  // 检查滚动容器
- testScroll()  // 测试滚动功能
- triggerScrollCheck()  // 手动触发滚动检查
- testCheckbox(0)  // 测试第一行的勾选
- testCustomCheckbox()  // 测试自定义checkbox
- testForceCheck(0)  // 强制勾选第一行
- testActiveClass(0)  // 测试CSS类添加
- testSupplementCheck(0)  // 测试补充勾选
- testCategoryMatch("袜子", "袜子,短袜")
- manualCheck()
            `);
        };

        // 测试自定义checkbox组件
        window.testCustomCheckbox = () => {
            console.log('🔍 测试自定义checkbox组件...');
            
            // 查找所有自定义checkbox
            const labels = document.querySelectorAll('label[data-testid="beast-core-checkbox"]');
            console.log('找到自定义checkbox数量:', labels.length);
            
            if (labels.length === 0) {
                console.log('❌ 未找到自定义checkbox');
                return;
            }
            
            // 测试第一个checkbox
            const firstLabel = labels[0];
            console.log('第一个checkbox:', firstLabel);
            console.log('当前data-checked:', firstLabel.getAttribute('data-checked'));
            
            // 查找相关元素
            const input = firstLabel.querySelector('input[type="checkbox"]');
            const square = firstLabel.querySelector('.CBX_square_5-118-0');
            const icon = firstLabel.querySelector('.CBX_iconCheck_5-118-0');
            
            console.log('相关元素:', {
                input: input,
                square: square,
                icon: icon,
                inputChecked: input ? input.checked : 'N/A',
                squareClasses: square ? square.className : 'N/A'
            });
            
            // 尝试切换状态
            const currentState = firstLabel.getAttribute('data-checked') === 'true';
            const newState = !currentState;
            
            console.log(`切换状态: ${currentState} -> ${newState}`);
            
            // 修改状态
            firstLabel.setAttribute('data-checked', newState.toString());
            if (input) {
                input.checked = newState;
            }
            
            // 添加或移除勾选样式
            if (square) {
                if (newState) {
                    square.classList.add('CBX_checked_5-118-0');
                } else {
                    square.classList.remove('CBX_checked_5-118-0');
                }
            }
            
            console.log('切换后状态:', {
                dataChecked: firstLabel.getAttribute('data-checked'),
                inputChecked: input ? input.checked : 'N/A',
                squareClasses: square ? square.className : 'N/A'
            });
            
            return { label: firstLabel, input, square, icon };
        };

        // 测试强制勾选
        window.testForceCheck = (rowIndex = 0) => {
            console.log('🔧 测试强制勾选...');
            
            const rows = document.querySelectorAll('tr[data-testid="beast-core-table-body-tr"]');
            if (rows.length === 0) {
                console.log('❌ 未找到表格行');
                return;
            }
            
            const row = rows[rowIndex];
            if (!row) {
                console.log(`❌ 未找到第${rowIndex}行`);
                return;
            }
            
            if (window.autoCheckManager && window.autoCheckManager.forceCheckRow) {
                window.autoCheckManager.forceCheckRow(row);
            } else {
                console.log('❌ 插件管理器未找到或没有forceCheckRow方法');
            }
        };

        // 测试CSS类添加
        window.testActiveClass = (rowIndex = 0) => {
            console.log('🔧 测试CSS类添加...');
            
            const rows = document.querySelectorAll('tr[data-testid="beast-core-table-body-tr"]');
            if (rows.length === 0) {
                console.log('❌ 未找到表格行');
                return;
            }
            
            const row = rows[rowIndex];
            if (!row) {
                console.log(`❌ 未找到第${rowIndex}行`);
                return;
            }
            
            const label = row.querySelector('label[data-testid="beast-core-checkbox"]');
            if (!label) {
                console.log('❌ 未找到checkbox label');
                return;
            }
            
            console.log('🔍 添加前的状态:');
            console.log('- label类名:', label.className);
            console.log('- data-checked:', label.getAttribute('data-checked'));
            
            const square = label.querySelector('.CBX_square_5-118-0');
            const icon = label.querySelector('.CBX_iconCheck_5-118-0');
            
            if (square) console.log('- square类名:', square.className);
            if (icon) console.log('- icon类名:', icon.className);
            
            // 添加激活类
            label.classList.add('CBX_active_5-118-0');
            if (square) square.classList.add('CBX_active_5-118-0');
            if (icon) icon.classList.add('CBX_active_5-118-0');
            
            console.log('🔍 添加后的状态:');
            console.log('- label类名:', label.className);
            console.log('- square类名:', square ? square.className : 'N/A');
            console.log('- icon类名:', icon ? icon.className : 'N/A');
            
            // 添加视觉反馈
            row.style.backgroundColor = '#e8f5e8';
            setTimeout(() => {
                row.style.backgroundColor = '';
            }, 3000);
            
            console.log('✅ CSS类添加完成');
        };

        // 测试补充勾选
        window.testSupplementCheck = (rowIndex = 0) => {
            console.log('🔧 测试补充勾选...');
            
            const rows = document.querySelectorAll('tr[data-testid="beast-core-table-body-tr"]');
            if (rows.length === 0) {
                console.log('❌ 未找到表格行');
                return;
            }
            
            const row = rows[rowIndex];
            if (!row) {
                console.log(`❌ 未找到第${rowIndex}行`);
                return;
            }
            
            if (window.autoCheckManager && window.autoCheckManager.supplementCheckRow) {
                window.autoCheckManager.supplementCheckRow(row);
            } else {
                console.log('❌ 插件管理器未找到或没有supplementCheckRow方法');
            }
        };

        console.log('🔧 调试命令已添加到控制台，输入 debugHelp() 查看帮助');
    }
}

// 初始化调试工具
const debugTool = new DebugTool(); 