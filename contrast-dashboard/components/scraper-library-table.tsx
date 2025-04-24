"use client"

import * as React from "react"
import {
  type ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
  getPaginationRowModel,
  type SortingState,
  getSortedRowModel,
} from "@tanstack/react-table"
import {
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  Clock,
  AlertTriangle,
  ArrowUpRight,
} from "lucide-react"
import { formatDistanceToNow, format } from "date-fns"

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"

interface ScraperRun {
  id: string
  timestamp: Date
  duration: number // in seconds
  status: "error" | "warning"
  message: string
  error: string
}

interface ScraperLibraryItem {
  id: string
  name: string
  health: "healthy" | "warning" | "broken"
  lastRan: Date | null
  lastModified: Date
  description?: string
  runs?: ScraperRun[]
}

// Dummy data for scraper runs - only errors and warnings
const generateDummyRuns = (scraperId: string, scraperName: string): ScraperRun[] => {
  const runs: ScraperRun[] = []

  // Generate 10 runs with errors and warnings
  for (let i = 0; i < 10; i++) {
    const daysAgo = i * 3 // Every 3 days
    const hoursVariation = Math.floor(Math.random() * 12) // Random hour in the day

    const timestamp = new Date()
    timestamp.setDate(timestamp.getDate() - daysAgo)
    timestamp.setHours(hoursVariation)

    const duration = Math.floor(Math.random() * 600) + 30 // 30 to 630 seconds

    // Alternate between errors and warnings
    const status = i % 2 === 0 ? "error" : "warning"
    let message: string
    let error: string

    if (status === "error") {
      message = "Scraper failed with critical error"
      error = `
ERROR: ConnectionError at ${timestamp.toISOString()}
Traceback (most recent call last):
  File "/app/scrapers/${scraperName}.py", line 142, in run_scraper
    response = session.get(url, timeout=30)
  File "/usr/local/lib/python3.9/site-packages/requests/sessions.py", line 555, in get
    return self.request('GET', url, **kwargs)
  File "/usr/local/lib/python3.9/site-packages/requests/sessions.py", line 542, in request
    resp = self.send(prep, **send_kwargs)
  File "/usr/local/lib/python3.9/site-packages/requests/sessions.py", line 655, in send
    r = adapter.send(request, **kwargs)
  File "/usr/local/lib/python3.9/site-packages/requests/adapters.py", line 498, in send
    raise ConnectionError(err, request=request)
requests.exceptions.ConnectionError: HTTPConnectionPool(host='example.com', port=80): Max retries exceeded with url: /products (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7f8b5d4b7a00>: Failed to establish a new connection: [Errno 111] Connection refused'))
      `
    } else {
      message = "Scraper completed with warnings"
      error = `
WARNING: TimeoutWarning at ${timestamp.toISOString()}
Some requests timed out during scraping:
- https://example.com/products/1234 (timeout after 15s)
- https://example.com/products/5678 (timeout after 15s)
Scraper continued with available data.
      `
    }

    runs.push({
      id: `${scraperId}-run-${i}`,
      timestamp,
      duration,
      status,
      message,
      error,
    })
  }

  // Sort by timestamp, newest first
  return runs.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
}

export function ScraperLibraryTable({ data }: { data: ScraperLibraryItem[] }) {
  const [sorting, setSorting] = React.useState<SortingState>([{ id: "name", desc: false }])
  const [selectedScraper, setSelectedScraper] = React.useState<ScraperLibraryItem | null>(null)
  const [isDialogOpen, setIsDialogOpen] = React.useState(false)

  const handleRowClick = (scraper: ScraperLibraryItem) => {
    // Generate runs data if not already present
    if (!scraper.runs) {
      scraper.runs = generateDummyRuns(scraper.id, scraper.name)
    }

    setSelectedScraper(scraper)
    setIsDialogOpen(true)
  }

  const columns: ColumnDef<ScraperLibraryItem>[] = [
    {
      accessorKey: "name",
      header: "Name of Scraper",
      cell: ({ row }) => (
        <div className="font-medium cursor-pointer hover:underline" onClick={() => handleRowClick(row.original)}>
          {row.getValue("name")}
        </div>
      ),
    },
    {
      accessorKey: "health",
      header: "Health",
      cell: ({ row }) => {
        const health = row.getValue("health") as string

        if (health === "healthy") {
          return <Badge className="bg-green-100 text-green-800 hover:bg-green-100 hover:text-green-800">Healthy</Badge>
        } else if (health === "warning") {
          return (
            <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100 hover:text-yellow-800">Warning</Badge>
          )
        } else {
          return <Badge variant="destructive">Broken</Badge>
        }
      },
    },
    {
      accessorKey: "lastRan",
      header: "Last Ran",
      cell: ({ row }) => {
        const date = row.getValue("lastRan") as Date | null
        if (!date) return <span className="text-muted-foreground">Never</span>

        return (
          <div className="flex flex-col">
            <span>{format(date, "MMM d, yyyy HH:mm:ss")}</span>
            <span className="text-xs text-muted-foreground">{formatDistanceToNow(date, { addSuffix: true })}</span>
          </div>
        )
      },
    },
    {
      accessorKey: "lastModified",
      header: "Last Modified",
      cell: ({ row }) => {
        const date = row.getValue("lastModified") as Date
        return (
          <div className="flex flex-col">
            <span>{format(date, "MMM d, yyyy HH:mm:ss")}</span>
            <span className="text-xs text-muted-foreground">{formatDistanceToNow(date, { addSuffix: true })}</span>
          </div>
        )
      },
    },
    {
      id: "actions",
      cell: () => (
        <div className="opacity-0 group-hover:opacity-100 transition-opacity flex justify-end">
          <ArrowUpRight className="h-4 w-4 text-muted-foreground" />
        </div>
      ),
    },
  ]

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onSortingChange: setSorting,
    getSortedRowModel: getSortedRowModel(),
    state: {
      sorting,
    },
    initialState: {
      pagination: {
        pageSize: 10,
      },
    },
  })

  return (
    <>
      <Card className="mx-4 lg:mx-6">
        <CardHeader>
          <CardTitle>Scraper Library</CardTitle>
          <CardDescription>Available scrapers and their current status</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                {table.getHeaderGroups().map((headerGroup) => (
                  <TableRow key={headerGroup.id}>
                    {headerGroup.headers.map((header) => (
                      <TableHead key={header.id}>
                        {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                      </TableHead>
                    ))}
                  </TableRow>
                ))}
              </TableHeader>
              <TableBody>
                {table.getRowModel().rows?.length ? (
                  table.getRowModel().rows.map((row) => (
                    <TableRow
                      key={row.id}
                      data-state={row.getIsSelected() && "selected"}
                      className="group cursor-pointer hover:bg-muted/50"
                      onClick={() => handleRowClick(row.original)}
                    >
                      {row.getVisibleCells().map((cell) => (
                        <TableCell key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</TableCell>
                      ))}
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={columns.length} className="h-24 text-center">
                      No results.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
          <div className="flex items-center justify-between space-x-2 py-4">
            <div className="flex items-center space-x-2">
              <p className="text-sm font-medium">Rows per page</p>
              <Select
                value={`${table.getState().pagination.pageSize}`}
                onValueChange={(value) => {
                  table.setPageSize(Number(value))
                }}
              >
                <SelectTrigger className="h-8 w-[70px]">
                  <SelectValue placeholder={table.getState().pagination.pageSize} />
                </SelectTrigger>
                <SelectContent side="top">
                  {[5, 10, 20, 30, 40, 50].map((pageSize) => (
                    <SelectItem key={pageSize} value={`${pageSize}`}>
                      {pageSize}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                className="hidden h-8 w-8 p-0 lg:flex"
                onClick={() => table.setPageIndex(0)}
                disabled={!table.getCanPreviousPage()}
              >
                <span className="sr-only">Go to first page</span>
                <ChevronsLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                className="h-8 w-8 p-0"
                onClick={() => table.previousPage()}
                disabled={!table.getCanPreviousPage()}
              >
                <span className="sr-only">Go to previous page</span>
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <div className="flex w-[100px] items-center justify-center text-sm font-medium">
                Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
              </div>
              <Button
                variant="outline"
                className="h-8 w-8 p-0"
                onClick={() => table.nextPage()}
                disabled={!table.getCanNextPage()}
              >
                <span className="sr-only">Go to next page</span>
                <ChevronRight className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                className="hidden h-8 w-8 p-0 lg:flex"
                onClick={() => table.setPageIndex(table.getPageCount() - 1)}
                disabled={!table.getCanNextPage()}
              >
                <span className="sr-only">Go to last page</span>
                <ChevronsRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="sm:max-w-[1200px] max-h-[1000] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {selectedScraper?.name}
              {selectedScraper?.health === "healthy" && <Badge className="bg-green-100 text-green-800">Healthy</Badge>}
              {selectedScraper?.health === "warning" && (
                <Badge className="bg-yellow-100 text-yellow-800">Warning</Badge>
              )}
              {selectedScraper?.health === "broken" && <Badge variant="destructive">Broken</Badge>}
            </DialogTitle>
            <DialogDescription>Error and warning history for this scraper</DialogDescription>
          </DialogHeader>

          <div className="flex-1 overflow-hidden">
            <ScrollArea className="h-[400px] w-full pr-4">
              <div className="space-y-4 pb-4">
                {selectedScraper?.runs?.map((run) => (
                  <Card
                    key={run.id}
                    className={
                      run.status === "error"
                        ? "border-red-200 bg-red-50"
                        : run.status === "warning"
                          ? "border-yellow-200 bg-yellow-50"
                          : ""
                    }
                  >
                    <CardHeader className="pb-2">
                      <div className="flex justify-between items-center">
                        <CardTitle className="text-base">{format(run.timestamp, "MMMM d, yyyy 'at' h:mm a")}</CardTitle>
                        <Badge
                          variant={run.status === "error" ? "destructive" : "outline"}
                          className={
                            run.status === "warning"
                              ? "bg-yellow-100 text-yellow-800 hover:bg-yellow-100 hover:text-yellow-800"
                              : ""
                          }
                        >
                          <AlertTriangle className="h-3 w-3 mr-1" />
                          {run.status.charAt(0).toUpperCase() + run.status.slice(1)}
                        </Badge>
                      </div>
                      <CardDescription className="flex items-center">
                        <Clock className="h-3 w-3 mr-1" />
                        Duration: {Math.floor(run.duration / 60)}m {run.duration % 60}s
                      </CardDescription>
                    </CardHeader>

                    <CardContent>
                      <p className="mb-2">{run.message}</p>

                      <div className="bg-black rounded-md p-4 text-white font-mono text-xs overflow-x-auto whitespace-pre-wrap">
                        {run.error}
                      </div>
                    </CardContent>

                    <CardFooter className="text-sm text-muted-foreground pt-0">Run ID: {run.id}</CardFooter>
                  </Card>
                ))}

                {(!selectedScraper?.runs || selectedScraper.runs.length === 0) && (
                  <div className="text-center py-8 text-muted-foreground">
                    No errors or warnings found for this scraper.
                  </div>
                )}
              </div>
            </ScrollArea>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}
