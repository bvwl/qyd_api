import { useState, useEffect, useRef } from 'react'
import { Card, Select, Spin, App, Button, Space } from 'antd'
import { ReloadOutlined, ClearOutlined } from '@ant-design/icons'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'
import { getProjectStatsForDashboard, clearStatsCache, getAvailableProjectsForStats } from '@/api/project'
import { useUserStore } from '@/store/useUserStore'

interface ProjectStatsData {
  project_id: string
  project_name: string
  dates: string[]
  counts: number[]
}

interface ProjectOption {
  id: string
  name: string
}

export default function ProjectStatsChart() {
  const { message } = App.useApp()
  const chartRef = useRef<HTMLDivElement>(null)
  const chartInstance = useRef<ECharts | null>(null)
  const [loading, setLoading] = useState(false)
  const [days, setDays] = useState(7)
  const [data, setData] = useState<ProjectStatsData[]>([])
  const [selectedProjects, setSelectedProjects] = useState<string[]>([])
  const [availableProjects, setAvailableProjects] = useState<ProjectOption[]>([])
  const userInfo = useUserStore((state) => state.userInfo)

  // 初始化图表
  useEffect(() => {
    if (chartRef.current && !chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current)
      
      // 监听窗口大小变化
      const handleResize = () => {
        chartInstance.current?.resize()
      }
      window.addEventListener('resize', handleResize)
      
      return () => {
        window.removeEventListener('resize', handleResize)
        chartInstance.current?.dispose()
        chartInstance.current = null
      }
    }
  }, [])

  // 加载可用项目列表
  useEffect(() => {
    loadAvailableProjects()
  }, [])

  // 加载数据
  useEffect(() => {
    loadData()
  }, [days, selectedProjects])

  const loadAvailableProjects = async () => {
    try {
      const response = await getAvailableProjectsForStats()
      if (response.code === 1 && response.data) {
        setAvailableProjects(response.data)
      }
    } catch (error: any) {
      console.error('加载项目列表失败:', error)
    }
  }

  const loadData = async () => {
    try {
      setLoading(true)
      
      // 构建请求参数
      const params: any = { days }
      if (selectedProjects.length > 0) {
        params.project_ids = selectedProjects.join(',')
      }
      
      const response = await getProjectStatsForDashboard(params)
      
      if (response.code === 1 && response.data) {
        setData(response.data)
        renderChart(response.data)
      } else {
        message.error(response.message || '加载统计数据失败')
      }
    } catch (error: any) {
      console.error('加载统计数据失败:', error)
      message.error(error.message || '加载统计数据失败')
    } finally {
      setLoading(false)
    }
  }

  const renderChart = (statsData: ProjectStatsData[]) => {
    if (!chartInstance.current || !statsData || statsData.length === 0) {
      return
    }

    // 配置图表
    const option: echarts.EChartsOption = {
      title: {
        text: selectedProjects.length > 0 ? '项目账号更新趋势' : '所有项目账号更新总和',
        left: 'center',
        textStyle: {
          fontSize: 16,
          fontWeight: 'normal'
        }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
          label: {
            backgroundColor: '#6a7985'
          }
        },
        formatter: (params: any) => {
          if (!Array.isArray(params)) return ''
          
          let result = `<div style="font-weight: bold; margin-bottom: 8px;">${params[0].axisValue}</div>`
          params.forEach((param: any) => {
            result += `
              <div style="display: flex; justify-content: space-between; align-items: center; margin: 4px 0;">
                <span>
                  ${param.marker}
                  <span style="margin-right: 16px;">${param.seriesName}</span>
                </span>
                <span style="font-weight: bold;">${param.value} 个</span>
              </div>
            `
          })
          return result
        }
      },
      legend: {
        data: statsData.map(item => item.project_name),
        top: 35,
        type: 'scroll',
        pageButtonPosition: 'end'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: statsData[0]?.dates || [],
        axisLabel: {
          rotate: 45,
          formatter: (value: string) => {
            // 格式化日期显示
            const date = new Date(value)
            return `${date.getMonth() + 1}/${date.getDate()}`
          }
        }
      },
      yAxis: {
        type: 'value',
        name: '更新数量',
        minInterval: 1,
        axisLabel: {
          formatter: '{value} 个'
        }
      },
      series: statsData.map(item => ({
        name: item.project_name,
        type: 'line',
        data: item.counts,
        smooth: true,
        emphasis: {
          focus: 'series'
        },
        lineStyle: {
          width: selectedProjects.length === 0 ? 3 : 2  // 总和曲线更粗
        },
        showSymbol: true,
        symbolSize: selectedProjects.length === 0 ? 8 : 6,
        // 如果是总和曲线，使用特殊颜色
        ...(item.project_id === 'total' ? {
          itemStyle: {
            color: '#1890ff'
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [{
                offset: 0,
                color: 'rgba(24, 144, 255, 0.3)'
              }, {
                offset: 1,
                color: 'rgba(24, 144, 255, 0.05)'
              }]
            }
          }
        } : {})
      }))
    }

    chartInstance.current.setOption(option, true)
  }

  const handleClearCache = async () => {
    try {
      setLoading(true)
      const response = await clearStatsCache()
      
      if (response.code === 1) {
        message.success('缓存已清除')
        // 重新加载数据
        await loadData()
      } else {
        message.error(response.message || '清除缓存失败')
      }
    } catch (error: any) {
      console.error('清除缓存失败:', error)
      message.error(error.message || '清除缓存失败')
    } finally {
      setLoading(false)
    }
  }

  const handleProjectChange = (values: string[]) => {
    setSelectedProjects(values)
  }

  // 检查是否是管理员
  const isAdmin = userInfo?.roles?.some(role => role.code === 'ADMIN') || false

  return (
    <Card
      title="项目账号更新趋势"
      extra={
        <Space wrap>
          <Select
            mode="multiple"
            value={selectedProjects}
            onChange={handleProjectChange}
            placeholder="选择项目（不选则显示总和）"
            style={{ width: 300 }}
            maxTagCount="responsive"
            allowClear
            showSearch
            filterOption={(input, option) =>
              (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
            }
            options={availableProjects.map(p => ({
              label: p.name,
              value: p.id
            }))}
          />
          <Select
            value={days}
            onChange={setDays}
            style={{ width: 120 }}
            options={[
              { label: '最近7天', value: 7 },
              { label: '最近14天', value: 14 },
              { label: '最近30天', value: 30 },
              { label: '最近90天', value: 90 }
            ]}
          />
          <Button
            icon={<ReloadOutlined />}
            onClick={loadData}
            loading={loading}
          >
            刷新
          </Button>
          {isAdmin && (
            <Button
              icon={<ClearOutlined />}
              onClick={handleClearCache}
              loading={loading}
            >
              清除缓存
            </Button>
          )}
        </Space>
      }
    >
      <Spin spinning={loading}>
        <div
          ref={chartRef}
          style={{
            width: '100%',
            height: 400,
            minHeight: 400
          }}
        />
        {data.length === 0 && !loading && (
          <div style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}>
            暂无统计数据
          </div>
        )}
      </Spin>
    </Card>
  )
}
