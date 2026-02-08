"use client"

import { useState, useMemo, useEffect } from "react"
import { Search, X, SlidersHorizontal, ChevronLeft, ChevronRight } from "lucide-react"
import { Input } from "./ui/input"
import { Button } from "./ui/button"
import { ProductCard } from "./ProductCard"
import { Product } from "@/lib/notion"
import {
  filterProducts,
  getUniqueBrands,
} from "@/lib/utils"
import { Badge } from "./ui/badge"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select"
import { Checkbox } from "./ui/checkbox"
import { RadioGroup, RadioGroupItem } from "./ui/radio-group"
import { Label } from "./ui/label"

interface ProductGridProps {
  products: Product[]
}

export function ProductGrid({ products }: ProductGridProps) {
  const [search, setSearch] = useState("")
  const [selectedBrand, setSelectedBrand] = useState<string | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [selectedGenders, setSelectedGenders] = useState<string[]>([])
  const [selectedRidingStyles, setSelectedRidingStyles] = useState<string[]>([])
  const [showFilters, setShowFilters] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const [rowsPerPage, setRowsPerPage] = useState(25)

  const brands = useMemo(() => getUniqueBrands(products), [products])

  const filteredProducts = useMemo(
    () =>
      filterProducts(products, {
        brand: selectedBrand || undefined,
        category: selectedCategory || undefined,
        genders: selectedGenders.length > 0 ? selectedGenders : undefined,
        ridingStyles: selectedRidingStyles.length > 0 ? selectedRidingStyles : undefined,
        search: search || undefined,
      }).sort((a, b) => a.price - b.price),
    [products, search, selectedBrand, selectedCategory, selectedGenders, selectedRidingStyles]
  )

  const activeFilterCount = [
    selectedBrand,
    selectedCategory,
    selectedGenders.length > 0,
    selectedRidingStyles.length > 0,
  ].filter(Boolean).length

  const hasAnyFilters = activeFilterCount > 0 || search

  // Pagination calculations
  const totalPages = Math.ceil(filteredProducts.length / rowsPerPage)
  const startIndex = (currentPage - 1) * rowsPerPage
  const paginatedProducts = filteredProducts.slice(startIndex, startIndex + rowsPerPage)

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1)
  }, [filteredProducts.length])

  const clearAllFilters = () => {
    setSelectedBrand(null)
    setSelectedCategory(null)
    setSelectedGenders([])
    setSelectedRidingStyles([])
    setSearch("")
  }

  return (
    <div className="w-full">
      <div className="flex flex-col lg:flex-row gap-8">
        {/* Sidebar Filters */}
        <aside
          aria-label="Product filters"
          id="product-filters"
          className={`lg:w-64 flex-shrink-0 ${
            showFilters ? "block" : "hidden lg:block"
          }`}
        >
          <div className="space-y-6 sticky top-24 bg-background lg:bg-transparent p-4 lg:p-0 rounded-xl lg:rounded-none border lg:border-0 border-border">
            {/* Search */}
            <div role="search">
              <label htmlFor="product-search" className="text-sm font-semibold text-foreground mb-3 block">Search</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" aria-hidden="true" />
                <Input
                  id="product-search"
                  type="search"
                  placeholder="Search products..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-9"
                  aria-describedby="search-description"
                />
                <span id="search-description" className="sr-only">Search by product name, brand, or description</span>
                {search && (
                  <button
                    onClick={() => setSearch("")}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    aria-label="Clear search"
                    type="button"
                  >
                    <X className="h-4 w-4" aria-hidden="true" />
                  </button>
                )}
              </div>
            </div>

            {/* Divider */}
            <div className="border-t border-border" />

            {/* Category Filter */}
            <fieldset>
              <legend className="text-sm font-semibold text-foreground mb-3 block">Category</legend>
              <RadioGroup
                value={selectedCategory || "all"}
                onValueChange={(value) => setSelectedCategory(value === "all" ? null : value)}
                className="space-y-2"
              >
                <div className="flex items-center space-x-3">
                  <RadioGroupItem value="all" id="category-all" />
                  <Label htmlFor="category-all" className="text-sm font-medium cursor-pointer">
                    All Categories
                  </Label>
                </div>
                {["Gloves", "Jackets", "Boots", "Pants", "Racing Suits", "Protection", "Street wear"].map((category) => (
                  <div key={category} className="flex items-center space-x-3">
                    <RadioGroupItem value={category} id={`category-${category}`} />
                    <Label htmlFor={`category-${category}`} className="text-sm font-medium cursor-pointer">
                      {category}
                    </Label>
                  </div>
                ))}
              </RadioGroup>
            </fieldset>

            {/* Gender Filter */}
            <fieldset>
              <legend className="text-sm font-semibold text-foreground mb-3 block">Gender</legend>
              <div className="space-y-2">
                {["Women", "Men", "Unisex"].map((gender) => (
                  <div key={gender} className="flex items-center space-x-3">
                    <Checkbox
                      id={`gender-${gender}`}
                      checked={selectedGenders.includes(gender)}
                      onCheckedChange={(checked) => {
                        setSelectedGenders(prev =>
                          checked
                            ? [...prev, gender]
                            : prev.filter(g => g !== gender)
                        )
                      }}
                    />
                    <Label htmlFor={`gender-${gender}`} className="text-sm font-medium cursor-pointer">
                      {gender}
                    </Label>
                  </div>
                ))}
              </div>
            </fieldset>

            {/* Riding Style Filter */}
            <fieldset>
              <legend className="text-sm font-semibold text-foreground mb-3 block">Riding Style</legend>
              <div className="space-y-2">
                {["Commute / Street", "Adventure / Touring", "Sport / Canyons", "Racing / Trackdays", "Off-roading"].map((style) => (
                  <div key={style} className="flex items-center space-x-3">
                    <Checkbox
                      id={`style-${style}`}
                      checked={selectedRidingStyles.includes(style)}
                      onCheckedChange={(checked) => {
                        setSelectedRidingStyles(prev =>
                          checked
                            ? [...prev, style]
                            : prev.filter(s => s !== style)
                        )
                      }}
                    />
                    <Label htmlFor={`style-${style}`} className="text-sm font-medium cursor-pointer">
                      {style}
                    </Label>
                  </div>
                ))}
              </div>
            </fieldset>

            {/* Brand Filter */}
            <fieldset>
              <legend className="text-sm font-semibold text-foreground mb-3 block">Brand</legend>
              <RadioGroup
                value={selectedBrand || "all"}
                onValueChange={(value) => setSelectedBrand(value === "all" ? null : value)}
                className="space-y-2 max-h-48 overflow-y-auto"
              >
                <div className="flex items-center space-x-3">
                  <RadioGroupItem value="all" id="brand-all" />
                  <Label htmlFor="brand-all" className="text-sm font-medium cursor-pointer">
                    All {brands.length} Brands
                  </Label>
                </div>
                {brands.map((brand) => (
                  <div key={brand} className="flex items-center space-x-3">
                    <RadioGroupItem value={brand} id={`brand-${brand}`} />
                    <Label htmlFor={`brand-${brand}`} className="text-sm font-medium cursor-pointer">
                      {brand}
                    </Label>
                  </div>
                ))}
              </RadioGroup>
            </fieldset>

            {/* Clear Filters */}
            {hasAnyFilters && (
              <>
                <div className="border-t border-border" aria-hidden="true" />
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={clearAllFilters}
                  aria-label={`Clear all ${activeFilterCount} active filters`}
                >
                  <X className="h-4 w-4 mr-2" aria-hidden="true" />
                  Clear All Filters
                </Button>
              </>
            )}
          </div>
        </aside>

        {/* Main Content */}
        <section className="flex-1" aria-label="Product results">
          {/* Mobile Filter Toggle & Results Count */}
          <div className="flex items-center justify-between mb-6">
            <p className="text-sm text-muted-foreground" aria-live="polite" aria-atomic="true">
              Showing <span className="font-semibold text-foreground">
                {filteredProducts.length > 0 ? startIndex + 1 : 0}-{Math.min(startIndex + rowsPerPage, filteredProducts.length)}
              </span> of {filteredProducts.length} products
            </p>
            <Button
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
              className="lg:hidden"
              aria-expanded={showFilters}
              aria-controls="product-filters"
              aria-label={`${showFilters ? "Hide" : "Show"} filters${activeFilterCount > 0 ? `, ${activeFilterCount} active` : ""}`}
            >
              <SlidersHorizontal className="h-4 w-4 mr-2" aria-hidden="true" />
              Filters
              {activeFilterCount > 0 && (
                <Badge variant="default" className="ml-2 h-5 w-5 p-0 flex items-center justify-center text-xs" aria-hidden="true">
                  {activeFilterCount}
                </Badge>
              )}
            </Button>
          </div>

          {/* Active Filters Display */}
          {hasAnyFilters && (
            <div className="mb-6 flex flex-wrap items-center gap-2" role="region" aria-label="Active filters">
              <span className="text-sm text-muted-foreground" id="active-filters-label">Active:</span>
              {selectedBrand && (
                <Badge variant="secondary" className="gap-1">
                  {selectedBrand}
                  <button
                    onClick={() => setSelectedBrand(null)}
                    className="ml-1 hover:text-foreground"
                    aria-label={`Remove ${selectedBrand} brand filter`}
                    type="button"
                  >
                    <X className="h-3 w-3" aria-hidden="true" />
                  </button>
                </Badge>
              )}
              {selectedCategory && (
                <Badge variant="secondary" className="gap-1">
                  {selectedCategory}
                  <button
                    onClick={() => setSelectedCategory(null)}
                    className="ml-1 hover:text-foreground"
                    aria-label={`Remove ${selectedCategory} category filter`}
                    type="button"
                  >
                    <X className="h-3 w-3" aria-hidden="true" />
                  </button>
                </Badge>
              )}
              {selectedGenders.map((gender) => (
                <Badge key={gender} variant="secondary" className="gap-1">
                  {gender}
                  <button
                    onClick={() => setSelectedGenders(prev => prev.filter(g => g !== gender))}
                    className="ml-1 hover:text-foreground"
                    aria-label={`Remove ${gender} gender filter`}
                    type="button"
                  >
                    <X className="h-3 w-3" aria-hidden="true" />
                  </button>
                </Badge>
              ))}
              {selectedRidingStyles.map((style) => (
                <Badge key={style} variant="secondary" className="gap-1">
                  {style}
                  <button
                    onClick={() => setSelectedRidingStyles(prev => prev.filter(s => s !== style))}
                    className="ml-1 hover:text-foreground"
                    aria-label={`Remove ${style} riding style filter`}
                    type="button"
                  >
                    <X className="h-3 w-3" aria-hidden="true" />
                  </button>
                </Badge>
              ))}
              {search && (
                <Badge variant="secondary" className="gap-1">
                  &quot;{search}&quot;
                  <button
                    onClick={() => setSearch("")}
                    className="ml-1 hover:text-foreground"
                    aria-label={`Remove search for "${search}"`}
                    type="button"
                  >
                    <X className="h-3 w-3" aria-hidden="true" />
                  </button>
                </Badge>
              )}
              <button
                onClick={clearAllFilters}
                className="text-sm text-muted-foreground hover:text-foreground underline"
                type="button"
              >
                Clear all
              </button>
            </div>
          )}

          {/* Products Grid */}
          {filteredProducts.length === 0 ? (
            <div className="text-center py-16 bg-muted/30 rounded-2xl">
              <p className="text-lg text-muted-foreground mb-4">No products found matching your filters.</p>
              <Button variant="outline" onClick={clearAllFilters}>
                Clear Filters
              </Button>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {paginatedProducts.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>

              {/* Pagination */}
              <nav aria-label="Product pagination" className="flex flex-col sm:flex-row items-center justify-between gap-4 mt-8 pt-6 border-t border-border">
                <div className="flex items-center gap-2">
                  <label htmlFor="rows-per-page" className="text-sm text-muted-foreground">Rows per page</label>
                  <Select
                    value={rowsPerPage.toString()}
                    onValueChange={(v) => {
                      setRowsPerPage(Number(v))
                      setCurrentPage(1)
                    }}
                  >
                    <SelectTrigger id="rows-per-page" className="w-[80px] h-9" aria-label={`${rowsPerPage} rows per page`}>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="25">25</SelectItem>
                      <SelectItem value="50">50</SelectItem>
                      <SelectItem value="100">100</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-center gap-2" role="group" aria-label="Pagination controls">
                  <span className="sr-only">Page {currentPage} of {totalPages}</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setCurrentPage(p => p - 1)}
                    disabled={currentPage === 1}
                    className="gap-1"
                    aria-label="Go to previous page"
                  >
                    <ChevronLeft className="h-4 w-4" aria-hidden="true" />
                    Previous
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setCurrentPage(p => p + 1)}
                    disabled={currentPage >= totalPages}
                    className="gap-1"
                    aria-label="Go to next page"
                  >
                    Next
                    <ChevronRight className="h-4 w-4" aria-hidden="true" />
                  </Button>
                </div>
              </nav>
            </>
          )}
        </section>
      </div>
    </div>
  )
}
