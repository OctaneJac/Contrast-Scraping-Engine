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
import { CheckCircle, Clock, AlertCircle, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from "lucide-react"
import { formatDistanceToNow, format } from "date-fns"

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface ScraperHistoryItem {
  scraper_name: string
  celery_trigger_time: Date
  actual_start_time: Date
  end_time: Date | null
  duration_seconds: number | null
  retries: number
  result: string | null
  error: string | null
}

export function ScraperHistoryTable({ data }: { data: ScraperHistoryItem[] }) {
  const [sorting, setSorting] = React.useState<SortingState>([{ id: "celery_trigger_time", desc: true }])

  const columns: ColumnDef<ScraperHistoryItem>[] = [
    {
      accessorKey: "scraper_name",
      header: "Scraper Name",
      cell: ({ row }) => <div className="font-medium">{row.getValue("scraper_name")}</div>,
    },
    {
      accessorKey: "celery_trigger_time",
      header: "Celery Trigger Time",
      cell: ({ row }) => {
        const date = row.getValue("celery_trigger_time") as Date
        return (
          <div className="flex flex-col">
            <span>{format(date, "MMM d, yyyy HH:mm:ss")}</span>
            <span className="text-xs text-muted-foreground">{formatDistanceToNow(date, { addSuffix: true })}</span>
          </div>
        )
      },
    },
    {
      accessorKey: "actual_start_time",
      header: "Actual Start Time",
      cell: ({ row }) => {
        const date = row.getValue("actual_start_time") as Date
        return (
          <div className="flex flex-col">
            <span>{format(date, "MMM d, yyyy HH:mm:ss")}</span>
            <span className="text-xs text-muted-foreground">{formatDistanceToNow(date, { addSuffix: true })}</span>
          </div>
        )
      },
    },
    {
      accessorKey: "end_time",
      header: "End Time",
      cell: ({ row }) => {
        const date = row.getValue("end_time") as Date | null
        if (!date) return <span className="text-muted-foreground">Not completed</span>

        return (
          <div className="flex flex-col">
            <span>{format(date, "MMM d, yyyy HH:mm:ss")}</span>
            <span className="text-xs text-muted-foreground">{formatDistanceToNow(date, { addSuffix: true })}</span>
          </div>
        )
      },
    },
    {
      accessorKey: "duration_seconds",
      header: "Duration",
      cell: ({ row }) => {
        const duration = row.getValue("duration_seconds") as number | null
        if (duration === null) return <span className="text-muted-foreground">N/A</span>

        const minutes = Math.floor(duration / 60)
        const seconds = Math.floor(duration % 60)
        return (
          <span>
            {minutes}m {seconds}s
          </span>
        )
      },
    },
    {
      accessorKey: "retries",
      header: "Retries",
      cell: ({ row }) => {
        const retries = row.getValue("retries") as number
        return <span>{retries}</span>
      },
    },
    {
      accessorKey: "result",
      header: "Result",
      cell: ({ row }) => {
        const result = row.getValue("result") as string | null
        const error = row.original.error

        if (error) {
          return (
            <Badge variant="destructive" className="flex items-center gap-1">
              <AlertCircle className="h-3 w-3" />
              Failed
            </Badge>
          )
        }

        if (!result) {
          return (
            <Badge variant="outline" className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              Running
            </Badge>
          )
        }

        return (
          <Badge
            variant="outline"
            className="flex items-center gap-1 bg-green-50 text-green-700 hover:bg-green-50 hover:text-green-700"
          >
            <CheckCircle className="h-3 w-3" />
            Success
          </Badge>
        )
      },
    },
    {
      accessorKey: "error",
      header: "Error",
      cell: ({ row }) => {
        const error = row.getValue("error") as string | null
        if (!error) return <span className="text-muted-foreground">None</span>

        return <span className="text-red-500">{error}</span>
      },
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
        pageSize: 5,
      },
    },
  })

  return (
    <Card className="mx-4 lg:mx-6">
      <CardHeader>
        <CardTitle>Scraper History</CardTitle>
        <CardDescription>Recent scraper runs and their status</CardDescription>
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
                  <TableRow key={row.id} data-state={row.getIsSelected() && "selected"}>
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
  )
}
