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
10. debugHelp() - 显示此帮助信息

示例用法:
- testPageElements()
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