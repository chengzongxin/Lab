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

                // 分析价格分布
        window.analyzePrices = () => {
            console.log('💰 分析页面价格分布...');
            
            if (window.autoCheckManager && window.autoCheckManager.analyzePriceDistribution) {
                const result = window.autoCheckManager.analyzePriceDistribution();
                
                console.log('📊 总体价格统计:', {
                    总商品数: result.stats.total,
                    最低价格: `¥${result.stats.min}`,
                    最高价格: `¥${result.stats.max}`,
                    平均价格: `¥${result.stats.avg.toFixed(2)}`
                });
                
                console.log('📈 按品类价格统计:');
                for (const [keyword, stats] of Object.entries(result.categoryStats)) {
                    console.log(`  ${keyword}:`, {
                        商品数量: stats.count,
                        最低价格: `¥${stats.min}`,
                        最高价格: `¥${stats.max}`,
                        平均价格: `¥${stats.avg.toFixed(2)}`,
                        价格范围: `${stats.prices.slice(0, 5).join(', ')}${stats.prices.length > 5 ? '...' : ''}`
                    });
                }
                
                // 建议最低价格设置
                console.log('💡 建议的最低价格设置:');
                for (const [keyword, stats] of Object.entries(result.categoryStats)) {
                    const suggestedPrice = Math.floor(stats.avg * 0.8); // 建议设为平均价格的80%
                    console.log(`  ${keyword}: 建议最低价 ¥${suggestedPrice} (当前平均价 ¥${stats.avg.toFixed(2)})`);
                }
                
                return result;
            } else {
                console.log('❌ 价格分析功能未找到');
                return null;
            }
        };

        // 测试关键词匹配
        window.testKeywordMatch = (productName, keyword) => {
            console.log('🔍 测试关键词匹配...');
            
            if (window.autoCheckManager) {
                const result = window.autoCheckManager.matchesCategory(productName, keyword);
                console.log(`测试结果: "${productName}" 匹配 "${keyword}" = ${result}`);
                
                // 详细分析匹配过程
                const name = productName.toLowerCase();
                const key = keyword.toLowerCase();
                
                console.log('匹配详情:');
                console.log(`  商品名称: "${name}"`);
                console.log(`  关键词: "${key}"`);
                console.log(`  直接匹配: ${name.includes(key)}`);
                
                if (key.endsWith('s')) {
                    const singular = key.slice(0, -1);
                    console.log(`  单数匹配: ${name.includes(singular)} (关键词: "${singular}")`);
                } else {
                    const plural = key + 's';
                    console.log(`  复数匹配: ${name.includes(plural)} (关键词: "${plural}")`);
                }
                
                if (key === 'drawstring bags') {
                    console.log(`  特殊匹配: ${name.includes('drawstring bag')} (关键词: "drawstring bag")`);
                }
                
                return result;
            } else {
                console.log('❌ 插件管理器未找到');
                return false;
            }
        };

        // 测试停止功能
        window.testStop = () => {
            console.log('🛑 测试停止功能...');
            
            if (window.autoCheckManager) {
                console.log('当前运行状态:', window.autoCheckManager.isRunning);
                console.log('当前定时器状态:', {
                    checkInterval: !!window.autoCheckManager.checkInterval,
                    scrollInterval: !!window.autoCheckManager.scrollInterval,
                    observer: !!window.autoCheckManager.observer
                });
                
                // 执行停止操作
                window.autoCheckManager.stopAutoCheck();
                
                // 延迟检查停止结果
                setTimeout(() => {
                    console.log('停止后状态检查:');
                    console.log('运行状态:', window.autoCheckManager.isRunning);
                    console.log('定时器状态:', {
                        checkInterval: !!window.autoCheckManager.checkInterval,
                        scrollInterval: !!window.autoCheckManager.scrollInterval,
                        observer: !!window.autoCheckManager.observer
                    });
                }, 1000);
            } else {
                console.log('❌ 插件管理器未找到');
            }
        };

        // 清理处理标记
        window.clearProcessedMarks = () => {
            console.log('🧹 清理所有处理标记...');
            
            const processedRows = document.querySelectorAll('[data-auto-check-processed]');
            const processingRows = document.querySelectorAll('[data-auto-check-processing]');
            
            processedRows.forEach(row => {
                row.removeAttribute('data-auto-check-processed');
            });
            
            processingRows.forEach(row => {
                row.removeAttribute('data-auto-check-processing');
            });
            
            console.log(`✅ 已清理 ${processedRows.length} 个已处理标记和 ${processingRows.length} 个处理中标记`);
            
            // 清理AutoCheckManager的processedRows
            if (window.autoCheckManager) {
                window.autoCheckManager.processedRows.clear();
                console.log('✅ 已清理插件内部的处理记录');
            }
        };

        // 手动创建批量权益按钮
        window.createBatchRightsButton = () => {
            console.log('🔧 手动创建批量权益按钮...');
            
            if (window.autoCheckManager) {
                window.autoCheckManager.createBatchRightsButton();
                console.log('✅ 批量权益按钮创建完成');
            } else {
                console.log('❌ 插件管理器未找到');
            }
        };

        // 诊断批量权益按钮问题
        window.diagnoseBatchRightsButton = () => {
            console.log('🔍 诊断批量权益按钮问题...');
            
            // 检查页面类型
            const pageType = window.autoCheckManager ? window.autoCheckManager.pageType : '未知';
            console.log('📄 当前页面类型:', pageType);
            
            // 检查提交按钮容器
            const submitBtnContainer = document.querySelector('.table-goods_footer__RXisB');
            console.log('📦 提交按钮容器:', submitBtnContainer ? '找到' : '未找到');
            if (submitBtnContainer) {
                console.log('容器内容:', submitBtnContainer.innerHTML.substring(0, 200) + '...');
            }
            
            // 检查原始提交按钮
            const originalSubmitBtn = document.querySelector('.table-goods_footer__RXisB button[data-testid="beast-core-button"]');
            console.log('🔘 原始提交按钮:', originalSubmitBtn ? '找到' : '未找到');
            if (originalSubmitBtn) {
                console.log('按钮文本:', originalSubmitBtn.textContent);
            }
            
            // 检查是否已有批量权益按钮
            const existingBtn = document.querySelector('#batch-rights-btn');
            console.log('🔘 批量权益按钮:', existingBtn ? '已存在' : '不存在');
            
            // 检查批量选择按钮
            const batchSelectLinks = document.querySelectorAll('th a[data-testid="beast-core-button-link"]');
            console.log('🔗 表头链接数量:', batchSelectLinks.length);
            batchSelectLinks.forEach((link, index) => {
                console.log(`  链接 ${index + 1}: "${link.textContent}"`);
            });
            
            // 检查是否在限时秒杀页面
            const flashSaleTitle = document.querySelector('.block-title-module__title___3MkQp');
            if (flashSaleTitle) {
                console.log('🎯 页面标题:', flashSaleTitle.textContent);
                console.log('📄 是否限时秒杀页面:', flashSaleTitle.textContent.includes('限时秒杀'));
            } else {
                console.log('❌ 未找到页面标题元素');
            }
            
            return {
                pageType,
                hasContainer: !!submitBtnContainer,
                hasOriginalBtn: !!originalSubmitBtn,
                hasExistingBtn: !!existingBtn,
                batchSelectLinksCount: batchSelectLinks.length,
                isFlashSalePage: flashSaleTitle ? flashSaleTitle.textContent.includes('限时秒杀') : false
            };
        };

        // 测试批量选择基础权益
        window.testBatchRights = async () => {
            console.log('🔧 测试批量选择基础权益...');
            
            if (window.autoCheckManager) {
                const success = await window.autoCheckManager.batchSelectBasicRights();
                console.log('测试结果:', success ? '成功' : '失败');
                return success;
            } else {
                console.log('❌ 插件管理器未找到');
                return false;
            }
        };

        // 手动启用提交按钮
        window.enableSubmitButton = () => {
            console.log('🔧 手动启用提交按钮...');
            
            if (window.autoCheckManager) {
                window.autoCheckManager.enableSubmitButton();
            } else {
                console.log('❌ 插件管理器未找到，尝试直接操作...');
                
                // 直接查找提交按钮
                const buttons = document.querySelectorAll('button[data-testid="beast-core-button"]');
                buttons.forEach((btn, index) => {
                    if (btn.textContent.includes('提交') && btn.id !== 'batch-rights-btn') {
                        console.log(`找到提交按钮 ${index}: "${btn.textContent}"`);
                        btn.disabled = false;
                        btn.style.opacity = '1';
                        btn.style.cursor = 'pointer';
                        btn.style.pointerEvents = 'auto';
                        btn.style.boxShadow = '0 0 0 2px #52c41a';
                        console.log('✅ 提交按钮已手动启用');
                    }
                });
            }
        };

        // 测试一键填入参考价
        window.testFillReferencePrice = async () => {
            console.log('🔧 测试一键填入参考价...');
            
            if (window.autoCheckManager) {
                const success = await window.autoCheckManager.clickFillReferencePrice();
                console.log('测试结果:', success ? '成功' : '失败');
                return success;
            } else {
                console.log('❌ 插件管理器未找到');
                return false;
            }
        };

        // 检查计数差异
        window.checkCountDifference = () => {
            console.log('🔍 检查计数差异...');
            
            // 获取所有表格行
            const allRows = document.querySelectorAll('tr[data-testid="beast-core-table-body-tr"]');
            console.log(`📊 总行数: ${allRows.length}`);
            
            // 检查实际勾选的行
            let actualCheckedCount = 0;
            const checkedRows = [];
            
            allRows.forEach((row, index) => {
                const checkbox = row.querySelector('label[data-testid="beast-core-checkbox"]');
                if (checkbox) {
                    const isChecked = checkbox.getAttribute('data-checked') === 'true';
                    if (isChecked) {
                        actualCheckedCount++;
                        
                        // 获取商品名称用于调试
                        let productName = 'Unknown';
                        const titleElement = row.querySelector('.goods-info_title__yHBeG, .beast-core-ellipsis-1');
                        if (titleElement) {
                            productName = titleElement.textContent.trim().replace(/\{[^}]*\}/g, '').trim();
                            if (productName.length > 50) {
                                productName = productName.substring(0, 50) + '...';
                            }
                        }
                        
                        checkedRows.push({
                            index: index + 1,
                            name: productName
                        });
                    }
                }
            });
            
            // 获取插件内部计数
            const pluginCount = window.autoCheckManager ? window.autoCheckManager.checkedCount : 0;
            
            console.log('📈 计数对比:');
            console.log(`  页面实际勾选: ${actualCheckedCount} 个`);
            console.log(`  插件内部计数: ${pluginCount} 个`);
            console.log(`  差异: ${Math.abs(actualCheckedCount - pluginCount)} 个`);
            
            if (actualCheckedCount !== pluginCount) {
                console.warn('⚠️ 发现计数不一致！');
                
                if (window.autoCheckManager) {
                    console.log('🔧 同步计数...');
                    window.autoCheckManager.checkedCount = actualCheckedCount;
                    console.log('✅ 已将插件计数同步为页面实际勾选数');
                }
            } else {
                console.log('✅ 计数一致');
            }
            
            // 显示前10个已勾选的商品
            if (checkedRows.length > 0) {
                console.log('📋 已勾选的商品（前10个）:');
                checkedRows.slice(0, 10).forEach(item => {
                    console.log(`  ${item.index}. ${item.name}`);
                });
                
                if (checkedRows.length > 10) {
                    console.log(`  ... 还有 ${checkedRows.length - 10} 个`);
                }
            }
            
            return {
                totalRows: allRows.length,
                actualChecked: actualCheckedCount,
                pluginCount: pluginCount,
                difference: Math.abs(actualCheckedCount - pluginCount),
                checkedItems: checkedRows
            };
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

// 调试工具 - 在控制台中使用
// 防止重复声明
if (typeof window.debugTools === 'undefined') {
    window.debugTools = {
        // 检测页面类型
        detectPageType() {
            const hasWorryFree = document.querySelector('.worry-free-detail_table__unQvk');
            const hasOfficialPromotion = document.querySelector('.beast-core-ellipsis-1');
            const hasFlashSale = document.querySelector('.block-title-module__title___3MkQp');
            
            if (hasWorryFree) {
                console.log('🎯 检测到页面类型: 省心报');
                return '省心报';
            } else if (hasOfficialPromotion) {
                console.log('🎯 检测到页面类型: 官方大促');
                return '官方大促';
            } else if (hasFlashSale && hasFlashSale.textContent.includes('限时秒杀')) {
                console.log('🎯 检测到页面类型: 限时秒杀');
                return '限时秒杀';
            } else {
                console.log('❌ 未知页面类型');
                return '未知页面';
            }
        },

        // 检查页面元素
        checkPageElements() {
            console.log('🔍 检查页面元素...');
            
            // 检查商品名称元素
            const titleElements = document.querySelectorAll('.goods-info_title__yHBeG, .beast-core-ellipsis-1');
            console.log(`📦 找到商品名称元素: ${titleElements.length} 个`);
            
            titleElements.forEach((el, index) => {
                // 使用与content.js相同的逻辑提取文本
                let text = '';
                
                // 方法1：获取所有文本节点，排除style标签
                const walker = document.createTreeWalker(
                    el,
                    NodeFilter.SHOW_TEXT,
                    {
                        acceptNode: function(node) {
                            // 排除style标签内的文本
                            let parent = node.parentElement;
                            while (parent && parent !== el) {
                                if (parent.tagName === 'STYLE') {
                                    return NodeFilter.FILTER_REJECT;
                                }
                                parent = parent.parentElement;
                            }
                            return NodeFilter.FILTER_ACCEPT;
                        }
                    },
                    false
                );
                
                const textNodes = [];
                let node;
                while (node = walker.nextNode()) {
                    const nodeText = node.textContent.trim();
                    if (nodeText && !nodeText.includes('{') && !nodeText.includes('}')) {
                        textNodes.push(nodeText);
                    }
                }
                
                if (textNodes.length > 0) {
                    text = textNodes.join(' ').trim();
                } else {
                    // 方法2：直接获取textContent并清理
                    text = el.textContent.trim();
                    // 移除CSS样式代码和style标签内容
                    text = text.replace(/\{[^}]*\}/g, '').trim();
                    // 移除可能的style标签内容
                    text = text.replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '').trim();
                }
                
                console.log(`  ${index + 1}. "${text}"`);
            });
            
            // 检查价格元素
            const priceElements = document.querySelectorAll('td:nth-child(5)');
            console.log(`💰 找到价格元素: ${priceElements.length} 个`);
            
            priceElements.forEach((el, index) => {
                const text = el.textContent.trim();
                console.log(`  ${index + 1}. "${text}"`);
            });
            
            // 检查checkbox元素
            const checkboxElements = document.querySelectorAll('[data-testid="beast-core-checkbox"]');
            console.log(`☑️ 找到checkbox元素: ${checkboxElements.length} 个`);
            
            checkboxElements.forEach((el, index) => {
                const isChecked = el.getAttribute('data-checked') === 'true';
                console.log(`  ${index + 1}. 状态: ${isChecked ? '已勾选' : '未勾选'}`);
            });
        },

        // 测试商品名称匹配
        testProductMatch(keyword) {
            console.log(`🔍 测试关键词匹配: "${keyword}"`);
            
            const titleElements = document.querySelectorAll('.goods-info_title__yHBeG, .beast-core-ellipsis-1');
            let matchCount = 0;
            
            titleElements.forEach((el, index) => {
                // 使用与content.js相同的逻辑提取文本
                let productName = '';
                
                // 方法1：获取所有文本节点，排除style标签
                const walker = document.createTreeWalker(
                    el,
                    NodeFilter.SHOW_TEXT,
                    {
                        acceptNode: function(node) {
                            // 排除style标签内的文本
                            let parent = node.parentElement;
                            while (parent && parent !== el) {
                                if (parent.tagName === 'STYLE') {
                                    return NodeFilter.FILTER_REJECT;
                                }
                                parent = parent.parentElement;
                            }
                            return NodeFilter.FILTER_ACCEPT;
                        }
                    },
                    false
                );
                
                const textNodes = [];
                let node;
                while (node = walker.nextNode()) {
                    const nodeText = node.textContent.trim();
                    if (nodeText && !nodeText.includes('{') && !nodeText.includes('}')) {
                        textNodes.push(nodeText);
                    }
                }
                
                if (textNodes.length > 0) {
                    productName = textNodes.join(' ').trim();
                } else {
                    // 方法2：直接获取textContent并清理
                    productName = el.textContent.trim();
                    // 移除CSS样式代码和style标签内容
                    productName = productName.replace(/\{[^}]*\}/g, '').trim();
                    // 移除可能的style标签内容
                    productName = productName.replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '').trim();
                }
                
                const isMatch = productName.toLowerCase().includes(keyword.toLowerCase());
                
                console.log(`  ${index + 1}. "${productName}" - ${isMatch ? '✅ 匹配' : '❌ 不匹配'}`);
                
                if (isMatch) matchCount++;
            });
            
            console.log(`📊 匹配结果: ${matchCount}/${titleElements.length} 个商品匹配关键词 "${keyword}"`);
            return matchCount;
        },

        // 测试价格解析
        testPriceParsing() {
            console.log('💰 测试价格解析...');
            
            const priceElements = document.querySelectorAll('td:nth-child(5)');
            
            priceElements.forEach((el, index) => {
                const priceText = el.textContent.trim();
                const priceMatch = priceText.match(/[\d.]+/);
                const price = priceMatch ? parseFloat(priceMatch[0]) : 0;
                
                console.log(`  ${index + 1}. 原始文本: "${priceText}" -> 解析价格: ${price}`);
            });
        },

        // 测试checkbox勾选
        testCheckboxCheck() {
            console.log('☑️ 测试checkbox勾选功能...');
            
            const checkboxElements = document.querySelectorAll('[data-testid="beast-core-checkbox"]');
            
            checkboxElements.forEach((el, index) => {
                const beforeState = el.getAttribute('data-checked') === 'true';
                console.log(`  ${index + 1}. 勾选前状态: ${beforeState ? '已勾选' : '未勾选'}`);
                
                // 模拟勾选
                el.click();
                
                setTimeout(() => {
                    const afterState = el.getAttribute('data-checked') === 'true';
                    console.log(`  ${index + 1}. 勾选后状态: ${afterState ? '已勾选' : '未勾选'}`);
                }, 100);
            });
        },

        // 检查滚动容器
        checkScrollContainers() {
            console.log('📜 检查滚动容器...');
            
            // 查找所有可能的滚动容器
            const scrollContainers = document.querySelectorAll('[style*="overflow"], [class*="scroll"], [class*="table"], .ant-table-body, .el-table__body-wrapper');
            
            console.log(`找到 ${scrollContainers.length} 个可能的滚动容器:`);
            
            scrollContainers.forEach((container, index) => {
                const style = window.getComputedStyle(container);
                const hasScroll = style.overflow === 'auto' || style.overflow === 'scroll' || style.overflowY === 'auto' || style.overflowY === 'scroll';
                const scrollHeight = container.scrollHeight;
                const clientHeight = container.clientHeight;
                const canScroll = scrollHeight > clientHeight;
                
                console.log(`  ${index + 1}. 元素:`, container);
                console.log(`     overflow: ${style.overflow}, overflowY: ${style.overflowY}`);
                console.log(`     scrollHeight: ${scrollHeight}, clientHeight: ${clientHeight}`);
                console.log(`     可滚动: ${hasScroll && canScroll ? '✅ 是' : '❌ 否'}`);
            });
        },

        // 测试滚动功能
        testScroll() {
            console.log('📜 测试滚动功能...');
            
            // 方法1：查找表格容器并滚动
            const tableContainer = this.findTableContainer();
            if (tableContainer) {
                console.log('找到表格容器，执行滚动:', tableContainer);
                tableContainer.scrollTo({
                    top: tableContainer.scrollHeight,
                    behavior: 'smooth'
                });
            }
            
            // 方法2：查找所有可能的滚动容器
            const scrollContainers = document.querySelectorAll('[style*="overflow"], [class*="scroll"], [class*="table"], .ant-table-body, .el-table__body-wrapper');
            console.log('找到滚动容器数量:', scrollContainers.length);
            
            scrollContainers.forEach((container, index) => {
                if (container.scrollHeight > container.clientHeight) {
                    console.log(`滚动容器 ${index}:`, container);
                    container.scrollTo({
                        top: container.scrollHeight,
                        behavior: 'smooth'
                    });
                }
            });
            
            // 方法3：直接滚动页面
            const currentScrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const maxScrollTop = document.body.scrollHeight - window.innerHeight;
            
            console.log('页面滚动信息:', {
                currentScrollTop,
                maxScrollTop,
                documentHeight: document.body.scrollHeight,
                windowHeight: window.innerHeight
            });
            
            if (maxScrollTop > currentScrollTop) {
                window.scrollTo({
                    top: maxScrollTop,
                    behavior: 'smooth'
                });
            }
        },

        // 查找表格容器
        findTableContainer() {
            // 查找包含表格的容器
            const table = document.querySelector('table, [data-testid*="table"]');
            if (table) {
                // 向上查找可滚动的父容器
                let container = table.parentElement;
                while (container && container !== document.body) {
                    const style = window.getComputedStyle(container);
                    if (style.overflow === 'auto' || style.overflow === 'scroll' || style.overflowY === 'auto' || style.overflowY === 'scroll') {
                        return container;
                    }
                    container = container.parentElement;
                }
            }
            
            // 查找常见的表格容器类名
            const commonContainers = [
                '.ant-table-body',
                '.el-table__body-wrapper',
                '.table-container',
                '.scroll-container',
                '[class*="table"]',
                '[class*="scroll"]'
            ];
            
            for (const selector of commonContainers) {
                const container = document.querySelector(selector);
                if (container && container.scrollHeight > container.clientHeight) {
                    return container;
                }
            }
            
            return null;
        },

        // 显示帮助信息
        help() {
            console.log(`
🎯 活动申报助手 - 调试工具

可用命令:
• debugTools.detectPageType() - 检测页面类型
• debugTools.checkPageElements() - 检查页面元素
• debugTools.testProductMatch('关键词') - 测试商品名称匹配
• debugTools.testPriceParsing() - 测试价格解析
• debugTools.testCheckboxCheck() - 测试checkbox勾选
• debugTools.checkScrollContainers() - 检查滚动容器
• debugTools.testScroll() - 测试滚动功能
• analyzePrices() - 分析价格分布并给出建议
• testKeywordMatch('商品名称', '关键词') - 测试关键词匹配
• testStop() - 测试停止功能
• clearProcessedMarks() - 清理处理标记
• checkCountDifference() - 检查计数差异
• createBatchRightsButton() - 手动创建批量权益按钮
• testBatchRights() - 测试批量选择基础权益
• diagnoseBatchRightsButton() - 诊断批量权益按钮问题
• enableSubmitButton() - 手动启用提交按钮
• testFillReferencePrice() - 测试一键填入参考价
• debugTools.help() - 显示此帮助信息

示例:
• debugTools.testProductMatch('袜子') - 测试匹配包含"袜子"的商品
• debugTools.testProductMatch('围裙') - 测试匹配包含"围裙"的商品
• analyzePrices() - 分析当前页面所有商品的价格分布
            `);
        }
    };

    // 自动显示帮助信息
    console.log('🎯 活动申报助手调试工具已加载');
    console.log('输入 debugTools.help() 查看可用命令');
} 