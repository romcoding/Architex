import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { 
  Sparkles, 
  Send, 
  Lightbulb, 
  AlertTriangle, 
  CheckCircle, 
  TrendingUp,
  Brain,
  Zap,
  Target,
  Shield
} from 'lucide-react'

const AIOracle = () => {
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const suggestions = [
    {
      type: 'pattern',
      title: 'Consider API Gateway Pattern',
      description: 'For your microservices architecture, an API Gateway can provide centralized routing, authentication, and rate limiting.',
      confidence: 0.92,
      icon: Target,
      color: 'bg-blue-500'
    },
    {
      type: 'security',
      title: 'Implement Circuit Breaker',
      description: 'Add circuit breaker pattern to prevent cascade failures between your microservices.',
      confidence: 0.87,
      icon: Shield,
      color: 'bg-green-500'
    },
    {
      type: 'performance',
      title: 'Database Sharding Strategy',
      description: 'Consider horizontal sharding for your user database to handle the 10,000+ concurrent users requirement.',
      confidence: 0.79,
      icon: TrendingUp,
      color: 'bg-orange-500'
    }
  ]

  const insights = [
    {
      title: 'Architecture Complexity Score',
      value: '7.2/10',
      description: 'Your architecture has moderate complexity. Consider simplifying service boundaries.',
      trend: 'up'
    },
    {
      title: 'Estimated Cost',
      value: '$2,400/month',
      description: 'Based on AWS pricing for your specified requirements.',
      trend: 'stable'
    },
    {
      title: 'Risk Assessment',
      value: 'Medium',
      description: '3 potential risks identified in your current design.',
      trend: 'down'
    }
  ]

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setIsLoading(true)
    // Simulate AI processing
    setTimeout(() => {
      setIsLoading(false)
      setQuery('')
    }, 2000)
  }

  return (
    <div className="w-80 border-l border-border bg-background flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
            <Brain className="w-5 h-5 text-primary-foreground" />
          </div>
          <div>
            <h3 className="font-semibold">AI Oracle</h3>
            <p className="text-xs text-muted-foreground">Your architecture assistant</p>
          </div>
        </div>

        {/* Query Input */}
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            placeholder="Ask about your architecture..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1"
          />
          <Button type="submit" size="sm" disabled={isLoading}>
            {isLoading ? (
              <Sparkles className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </form>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {/* Quick Insights */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Zap className="w-4 h-4" />
              Quick Insights
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {insights.map((insight, index) => (
              <div key={index} className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">{insight.title}</span>
                  <Badge variant="outline" className="text-xs">
                    {insight.value}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground">{insight.description}</p>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* AI Suggestions */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Lightbulb className="w-4 h-4" />
              Suggestions
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {suggestions.map((suggestion, index) => (
              <div key={index} className="space-y-2">
                <div className="flex items-start gap-3">
                  <div className={`w-6 h-6 ${suggestion.color} rounded-full flex items-center justify-center flex-shrink-0`}>
                    <suggestion.icon className="w-3 h-3 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="text-sm font-medium">{suggestion.title}</h4>
                      <Badge variant="secondary" className="text-xs">
                        {Math.round(suggestion.confidence * 100)}%
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">{suggestion.description}</p>
                    <div className="flex gap-1 mt-2">
                      <Button variant="ghost" size="sm" className="h-6 text-xs">
                        Apply
                      </Button>
                      <Button variant="ghost" size="sm" className="h-6 text-xs">
                        Learn More
                      </Button>
                    </div>
                  </div>
                </div>
                {index < suggestions.length - 1 && <Separator />}
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm">Recent Activity</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-start gap-3">
              <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm">Applied API Gateway pattern</p>
                <p className="text-xs text-muted-foreground">2 minutes ago</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm">Identified potential bottleneck</p>
                <p className="text-xs text-muted-foreground">5 minutes ago</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Lightbulb className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm">Suggested caching strategy</p>
                <p className="text-xs text-muted-foreground">10 minutes ago</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button variant="outline" size="sm" className="w-full justify-start text-xs">
              <Sparkles className="w-3 h-3 mr-2" />
              Generate Architecture Diagram
            </Button>
            <Button variant="outline" size="sm" className="w-full justify-start text-xs">
              <Target className="w-3 h-3 mr-2" />
              Analyze Trade-offs
            </Button>
            <Button variant="outline" size="sm" className="w-full justify-start text-xs">
              <Shield className="w-3 h-3 mr-2" />
              Security Review
            </Button>
            <Button variant="outline" size="sm" className="w-full justify-start text-xs">
              <TrendingUp className="w-3 h-3 mr-2" />
              Cost Optimization
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default AIOracle
