// import { TrendingUpIcon } from "lucide-react"
import { formatDistanceToNow } from "date-fns"

// import { Badge } from "@/components/ui/badge"
import { Card, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"

interface DashboardStatsProps {
  lastScraped: Date | null
  totalScrapes: number
  totalProducts: number
  activeProducts: number
}

export function DashboardStats({ lastScraped, totalScrapes, totalProducts, activeProducts }: DashboardStatsProps) {
  // Format the dates as "X time ago" (e.g., "2 hours ago")
  const formatTimeAgo = (date: Date | null) => {
    if (!date) return "Never"
    return formatDistanceToNow(date, { addSuffix: true })
  }

  // Calculate active product percentage
  const activePercentage = totalProducts > 0 ? Math.round((activeProducts / totalProducts) * 100) : 0

  return (
    <div className="*:data-[slot=card]:shadow-xs @xl/main:grid-cols-2 @5xl/main:grid-cols-4 grid grid-cols-1 gap-4 px-4 *:data-[slot=card]:bg-gradient-to-t *:data-[slot=card]:from-primary/5 *:data-[slot=card]:to-card dark:*:data-[slot=card]:bg-card lg:px-6">
      <Card className="@container/card">
        <CardHeader className="relative">
          <CardDescription>Last Scraped</CardDescription>
          <CardTitle className="@[250px]/card:text-3xl text-2xl font-semibold">{formatTimeAgo(lastScraped)}</CardTitle>
          <div className="absolute right-4 top-4">
          </div>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1 text-sm">
          <div className="line-clamp-1 font-medium">
            {lastScraped ? new Date(lastScraped).toLocaleString() : "No data available"}
          </div>
          {/* <div className="text-muted-foreground">Last time all scrapers ran</div> */}
        </CardFooter>
      </Card>

      <Card className="@container/card">
        <CardHeader className="relative">
          <CardDescription>Total Scrapes</CardDescription>
          <CardTitle className="@[250px]/card:text-3xl text-2xl font-semibold">
            {totalScrapes.toLocaleString()}
          </CardTitle>
          <div className="absolute right-4 top-4">
            {/* <Badge variant="outline" className="flex gap-1 rounded-lg text-xs">
              <TrendingUpIcon className="size-3" />
              Latest
            </Badge> */}
          </div>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1 text-sm">
          <div className="line-clamp-1 font-medium">
            Scrapes performed in last 30 days
          </div>
          {/* <div className="text-muted-foreground">Total number of scrapes</div> */}
        </CardFooter>
      </Card>

      <Card className="@container/card">
        <CardHeader className="relative">
          <CardDescription>Total Products in DB</CardDescription>
          <CardTitle className="@[250px]/card:text-3xl text-2xl font-semibold tabular-nums">
            {totalProducts.toLocaleString()}
          </CardTitle>
          <div className="absolute right-4 top-4">
            {/* <Badge variant="outline" className="flex gap-1 rounded-lg text-xs">
              <TrendingUpIcon className="size-3" />
              Database
            </Badge> */}
          </div>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1 text-sm">
          <div className="line-clamp-1 flex gap-2 font-medium">Clothing products currently being tracked</div>
          {/* <div className="text-muted-foreground">Products stored in database</div> */}
        </CardFooter>
      </Card>

      <Card className="@container/card">
        <CardHeader className="relative">
          <CardDescription>Active Products</CardDescription>
          <CardTitle className="@[250px]/card:text-3xl text-2xl font-semibold tabular-nums">
            {activeProducts.toLocaleString()}
          </CardTitle>
          <div className="absolute right-4 top-4">
            {/* <Badge variant="outline" className="flex gap-1 rounded-lg text-xs">
              <TrendingUpIcon className="size-3" />
              {activePercentage}%
            </Badge> */}
          </div>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1 text-sm">
          <div className="line-clamp-1 flex gap-2 font-medium">{activePercentage}% of total products</div>
          {/* <div className="text-muted-foreground">Currently active products</div> */}
        </CardFooter>
      </Card>
    </div>
  )
}
