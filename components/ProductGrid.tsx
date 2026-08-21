"use client"

import { useState, useMemo, useEffect, useCallback, useRef } from "react"
import { useRouter, usePathname } from "next/navigation"
import { Search, X, SlidersHorizontal, ChevronLeft, ChevronRight } from "lucide-react"
import { Input } from "./ui/input"
import { Button } from "./ui/button"
import { ProductCard } from "./ProductCard"
import { Product } from "@/lib/notion"
import {
  filterProducts,
  getUniqueBrands,
  getUniqueValues,
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

const PRICE_RANGES = [
  { value: "0-100", label: "Under $100", min: 0, max: 100 },
  { value: "100-250", label: "$100 to $250", min: 100, max: 250 },
  { value: "250-500", label: "$250 to $500", min: 250, max: 500 },
  { value: "500-", label: "$500 and up", min: 500, max: undefined },
] as const

const SORT_OPTIONS = [
  { value: "updated", label: "Recently updated" },
  { value: "price-asc", label: "Price: Low to High" },
  { value: "price-desc", label: "Price: High to Low" },
  { value: "name", label: "Name: A to Z" },
] as const

type SortValue = (typeof SORT_OPTIONS)[number]["value"]

export function ProductGrid({ products }: ProductGridProps) {
  const router = useRouter()
  const pathname = usePathname()
  const resultsRef = useRef<HTMLElement>(null)

  const [search, setSearch] = useState("")
  const [selectedBrand, setSelectedBrand] = useState<string | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [selectedGenders, setSelectedGenders] = useState<string[]>([])
  const [selectedRidingStyles, setSelectedRidingStyles] = useState<string[]>([])
  const [selectedProtection, setSelectedProtection] = useState<string[]>([])
  const [selectedSeasons, setSelectedSeasons] = useState<string[]>([])
  const [selectedWaterproof, setSelectedWaterproof] = useState<string[]>([])
  const [selectedPriceRange, setSelectedPriceRange] = useState<string | null>(null)
  const [sortBy, setSortBy] = useState<SortValue>("updated")
  const [showFilters, setShowFilters] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const [rowsPerPage, setRowsPerPage] = useState(24)

  // Filters initialize empty so the server-rendered grid matches the first
  // client render (no useSearchParams — it would keep the whole grid out of
  // the static HTML). Deep-linked filter state is applied after mount.
  const [initialized, setInitialized] = useState(false)
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    setSearch(params.get("search") || "")
    setSelectedBrand(params.get("brand"))
    setSelectedCategory(params.get("category"))
    setSelectedGenders(params.get("gender")?.split(",").filter(Boolean) || [])
    setSelectedRidingStyles(params.get("style")?.split(",").filter(Boolean) || [])
    setSelectedProtection(params.get("protection")?.split(",").filter(Boolean) || [])
    setSelectedSeasons(params.get("season")?.split(",").filter(Boolean) || [])
    setSelectedWaterproof(params.get("waterproof")?.split(",").filter(Boolean) || [])
    const price = params.get("price")
    if (price && PRICE_RANGES.some((r) => r.value === price)) setSelectedPriceRange(price)
    const sort = params.get("sort")
    if (sort && SORT_OPTIONS.some((o) => o.value === sort)) setSortBy(sort as SortValue)
    const page = parseInt(params.get("page") || "1", 10)
    if (page > 1) setCurrentPage(page)
    setInitialized(true)
  }, [])

  // Sync filter state → URL params (only once the URL has been read)
  const syncUrl = useCallback(() => {
    if (!initialized) return
    const params = new URLSearchParams()
    if (search) params.set("search", search)
    if (selectedBrand) params.set("brand", selectedBrand)
    if (selectedCategory) params.set("category", selectedCategory)
    if (selectedGenders.length > 0) params.set("gender", selectedGenders.join(","))
    if (selectedRidingStyles.length > 0) params.set("style", selectedRidingStyles.join(","))
    if (selectedProtection.length > 0) params.set("protection", selectedProtection.join(","))
    if (selectedSeasons.length > 0) params.set("season", selectedSeasons.join(","))
    if (selectedWaterproof.length > 0) params.set("waterproof", selectedWaterproof.join(","))
    if (selectedPriceRange) params.set("price", selectedPriceRange)
    if (sortBy !== "updated") params.set("sort", sortBy)
    if (currentPage > 1) params.set("page", String(currentPage))
    const qs = params.toString()
    router.replace(`${pathname}${qs ? `?${qs}` : ""}`, { scroll: false })
  }, [initialized, search, selectedBrand, selectedCategory, selectedGenders, selectedRidingStyles, selectedProtection, selectedSeasons, selectedWaterproof, selectedPriceRange, sortBy, currentPage, pathname, router])

  useEffect(() => {
    syncUrl()
  }, [syncUrl])

  const brands = useMemo(() => getUniqueBrands(products), [products])
  const protectionLevels = useMemo(() => getUniqueValues(products, (p) => p.levelOfProtection), [products])
  const seasons = useMemo(() => getUniqueValues(products, (p) => p.season), [products])
  const waterproofLevels = useMemo(() => getUniqueValues(products, (p) => p.waterproofLevel), [products])

  const priceRange = PRICE_RANGES.find((r) => r.value === selectedPriceRange)

  const filteredProducts = useMemo(() => {
    const filtered = filterProducts(products, {
      brand: selectedBrand || undefined,
      category: selectedCategory || undefined,
      genders: selectedGenders.length > 0 ? selectedGenders : undefined,
      ridingStyles: selectedRidingStyles.length > 0 ? selectedRidingStyles : undefined,
      protectionLevels: selectedProtection.length > 0 ? selectedProtection : undefined,
      seasons: selectedSeasons.length > 0 ? selectedSeasons : undefined,
      waterproofLevels: selectedWaterproof.length > 0 ? selectedWaterproof : undefined,
      priceMin: priceRange?.min,
      priceMax: priceRange?.max,
      search: search || undefined,
    })
    switch (sortBy) {
      case "price-asc":
        return filtered.sort((a, b) => a.price - b.price)
      case "price-desc":
        return filtered.sort((a, b) => b.price - a.price)
      case "name":
        return filtered.sort((a, b) => a.name.localeCompare(b.name))
      default:
        return filtered.sort((a, b) => new Date(b.lastEditedTime).getTime() - new Date(a.lastEditedTime).getTime())
    }
  }, [products, search, selectedBrand, selectedCategory, selectedGenders, selectedRidingStyles, selectedProtection, selectedSeasons, selectedWaterproof, priceRange, sortBy])

  const activeFilterCount = [
    selectedBrand,
    selectedCategory,
    selectedGenders.length > 0,
    selectedRidingStyles.length > 0,
    selectedProtection.length > 0,
    selectedSeasons.length > 0,
    selectedWaterproof.length > 0,
    selectedPriceRange,
  ].filter(Boolean).length

  const hasAnyFilters = activeFilterCount > 0 || search

  // Pagination calculations
  const totalPages = Math.max(Math.ceil(filteredProducts.length / rowsPerPage), 1)
  const startIndex = (currentPage - 1) * rowsPerPage
  const paginatedProducts = filteredProducts.slice(startIndex, startIndex + rowsPerPage)

  // Heal out-of-range pages (stale ?page= deep links, shrinking result sets)
  useEffect(() => {
    if (currentPage > totalPages) setCurrentPage(totalPages)
  }, [currentPage, totalPages])

  // Page resets live in the change handlers (not an effect) so the
  // deep-linked ?page= value survives the post-mount URL initialization.
  const resetPage = () => setCurrentPage(1)

  const goToPage = (page: number) => {
    setCurrentPage(page)
    resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" })
  }

  const clearAllFilters = () => {
    setSelectedBrand(null)
    setSelectedCategory(null)
    setSelectedGenders([])
    setSelectedRidingStyles([])
    setSelectedProtection([])
    setSelectedSeasons([])
    setSelectedWaterproof([])
    setSelectedPriceRange(null)
    setSearch("")
    resetPage()
  }

  const checkboxFieldset = (
    legend: string,
    options: string[],
    selected: string[],
    setSelected: (update: (prev: string[]) => string[]) => void,
    idPrefix: string
  ) => (
    <fieldset>
      <legend className="text-sm font-semibold text-foreground mb-3 block">{legend}</legend>
      <div className="space-y-2">
        {options.map((option) => (
          <div key={option} className="flex items-center space-x-3">
            <Checkbox
              id={`${idPrefix}-${option}`}
              checked={selected.includes(option)}
              onCheckedChange={(checked) => {
                setSelected((prev) =>
                  checked ? [...prev, option] : prev.filter((v) => v !== option)
                )
                resetPage()
              }}
            />
            <Label htmlFor={`${idPrefix}-${option}`} className="text-sm font-medium cursor-pointer">
              {option}
            </Label>
          </div>
        ))}
      </div>
    </fieldset>
  )

  const filterChip = (label: string, onRemove: () => void, removeLabel: string) => (
    <Badge variant="secondary" className="gap-1">
      {label}
      <button
        onClick={() => {
          onRemove()
          resetPage()
        }}
        className="-mr-1 rounded p-1 hover:text-foreground"
        aria-label={removeLabel}
        type="button"
      >
        <X className="h-3 w-3" aria-hidden="true" />
      </button>
    </Badge>
  )

  return (
    <div className="w-full">
      <div className="flex flex-col lg:flex-row gap-8">
        <aside
          aria-label="Product filters"
          id="product-filters"
          className={`lg:w-64 flex-shrink-0 ${
            showFilters ? "block" : "hidden lg:block"
          }`}
        >
          <div className="space-y-6 sticky top-24 bg-background lg:bg-transparent p-4 lg:p-0 rounded-xl lg:rounded-none border lg:border-0 border-border max-h-[calc(100vh-7rem)] overflow-y-auto">
            <div role="search">
              <label htmlFor="product-search" className="text-sm font-semibold text-foreground mb-3 block">Search</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" aria-hidden="true" />
                <Input
                  id="product-search"
                  type="search"
                  placeholder="Search products..."
                  value={search}
                  onChange={(e) => {
                    setSearch(e.target.value)
                    resetPage()
                  }}
                  className="pl-9"
                  aria-describedby="search-description"
                />
                <span id="search-description" className="sr-only">Search by product name, brand, description, category, or material</span>
                {search && (
                  <button
                    onClick={() => {
                      setSearch("")
                      resetPage()
                    }}
                    className="absolute right-2 top-1/2 -translate-y-1/2 rounded p-1 text-muted-foreground hover:text-foreground"
                    aria-label="Clear search"
                    type="button"
                  >
                    <X className="h-4 w-4" aria-hidden="true" />
                  </button>
                )}
              </div>
            </div>

            <div className="border-t border-border" />

            <fieldset>
              <legend className="text-sm font-semibold text-foreground mb-3 block">Category</legend>
              <RadioGroup
                value={selectedCategory || "all"}
                onValueChange={(value) => {
                  setSelectedCategory(value === "all" ? null : value)
                  resetPage()
                }}
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

            <fieldset>
              <legend className="text-sm font-semibold text-foreground mb-3 block">Price</legend>
              <RadioGroup
                value={selectedPriceRange || "all"}
                onValueChange={(value) => {
                  setSelectedPriceRange(value === "all" ? null : value)
                  resetPage()
                }}
                className="space-y-2"
              >
                <div className="flex items-center space-x-3">
                  <RadioGroupItem value="all" id="price-all" />
                  <Label htmlFor="price-all" className="text-sm font-medium cursor-pointer">
                    Any Price
                  </Label>
                </div>
                {PRICE_RANGES.map((range) => (
                  <div key={range.value} className="flex items-center space-x-3">
                    <RadioGroupItem value={range.value} id={`price-${range.value}`} />
                    <Label htmlFor={`price-${range.value}`} className="text-sm font-medium cursor-pointer">
                      {range.label}
                    </Label>
                  </div>
                ))}
              </RadioGroup>
            </fieldset>

            {protectionLevels.length > 0 &&
              checkboxFieldset("Protection Level", protectionLevels, selectedProtection, setSelectedProtection, "protection")}

            {seasons.length > 0 &&
              checkboxFieldset("Season", seasons, selectedSeasons, setSelectedSeasons, "season")}

            {waterproofLevels.length > 0 &&
              checkboxFieldset("Waterproofing", waterproofLevels, selectedWaterproof, setSelectedWaterproof, "waterproof")}

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
                        resetPage()
                      }}
                    />
                    <Label htmlFor={`gender-${gender}`} className="text-sm font-medium cursor-pointer">
                      {gender}
                    </Label>
                  </div>
                ))}
              </div>
            </fieldset>

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
                        resetPage()
                      }}
                    />
                    <Label htmlFor={`style-${style}`} className="text-sm font-medium cursor-pointer">
                      {style}
                    </Label>
                  </div>
                ))}
              </div>
            </fieldset>

            <fieldset>
              <legend className="text-sm font-semibold text-foreground mb-3 block">Brand</legend>
              <RadioGroup
                value={selectedBrand || "all"}
                onValueChange={(value) => {
                  setSelectedBrand(value === "all" ? null : value)
                  resetPage()
                }}
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

        <section className="flex-1" aria-label="Product results" ref={resultsRef}>
          <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
            <p className="text-sm text-muted-foreground" aria-live="polite" aria-atomic="true">
              Showing <span className="font-semibold text-foreground">
                {filteredProducts.length > 0 ? startIndex + 1 : 0}-{Math.min(startIndex + rowsPerPage, filteredProducts.length)}
              </span> of {filteredProducts.length} products
            </p>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <label htmlFor="sort-products" className="text-sm text-muted-foreground whitespace-nowrap">Sort by</label>
                <Select
                  value={sortBy}
                  onValueChange={(v) => {
                    setSortBy(v as SortValue)
                    resetPage()
                  }}
                >
                  <SelectTrigger id="sort-products" className="h-9 w-44">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {SORT_OPTIONS.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
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
          </div>

          {hasAnyFilters && (
            <div className="mb-6 flex flex-wrap items-center gap-2" role="region" aria-label="Active filters">
              <span className="text-sm text-muted-foreground" id="active-filters-label">Active:</span>
              {selectedBrand &&
                filterChip(selectedBrand, () => setSelectedBrand(null), `Remove ${selectedBrand} brand filter`)}
              {selectedCategory &&
                filterChip(selectedCategory, () => setSelectedCategory(null), `Remove ${selectedCategory} category filter`)}
              {priceRange &&
                filterChip(priceRange.label, () => setSelectedPriceRange(null), `Remove ${priceRange.label} price filter`)}
              {selectedGenders.map((gender) =>
                <span key={gender}>{filterChip(gender, () => setSelectedGenders(prev => prev.filter(g => g !== gender)), `Remove ${gender} gender filter`)}</span>
              )}
              {selectedRidingStyles.map((style) =>
                <span key={style}>{filterChip(style, () => setSelectedRidingStyles(prev => prev.filter(s => s !== style)), `Remove ${style} riding style filter`)}</span>
              )}
              {selectedProtection.map((level) =>
                <span key={level}>{filterChip(level, () => setSelectedProtection(prev => prev.filter(l => l !== level)), `Remove ${level} protection filter`)}</span>
              )}
              {selectedSeasons.map((season) =>
                <span key={season}>{filterChip(season, () => setSelectedSeasons(prev => prev.filter(s => s !== season)), `Remove ${season} season filter`)}</span>
              )}
              {selectedWaterproof.map((level) =>
                <span key={level}>{filterChip(level, () => setSelectedWaterproof(prev => prev.filter(l => l !== level)), `Remove ${level} waterproofing filter`)}</span>
              )}
              {search &&
                filterChip(`"${search}"`, () => setSearch(""), `Remove search for "${search}"`)}
              <button
                onClick={clearAllFilters}
                className="text-sm text-muted-foreground hover:text-foreground underline"
                type="button"
              >
                Clear all
              </button>
            </div>
          )}

          {filteredProducts.length === 0 ? (
            <div className="text-center py-16 bg-muted/30 rounded-2xl">
              <p className="text-lg text-muted-foreground mb-2">No products match your search and filters.</p>
              <p className="text-sm text-muted-foreground mb-4">
                Try removing a filter or search term, or browse all categories.
              </p>
              <Button variant="outline" onClick={clearAllFilters}>
                Clear Filters
              </Button>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                {paginatedProducts.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>

              <nav aria-label="Product pagination" className="flex flex-col sm:flex-row items-center justify-between gap-4 mt-8 pt-6 border-t border-border">
                <div className="flex items-center gap-2">
                  <label htmlFor="rows-per-page" className="text-sm text-muted-foreground">Products per page</label>
                  <Select
                    value={rowsPerPage.toString()}
                    onValueChange={(v) => {
                      setRowsPerPage(Number(v))
                      resetPage()
                    }}
                  >
                    <SelectTrigger id="rows-per-page" className="w-20 h-9" aria-label={`${rowsPerPage} rows per page`}>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="24">24</SelectItem>
                      <SelectItem value="48">48</SelectItem>
                      <SelectItem value="96">96</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-center gap-3" role="group" aria-label="Pagination controls">
                  <span className="text-sm text-muted-foreground">Page {currentPage} of {totalPages}</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => goToPage(currentPage - 1)}
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
                    onClick={() => goToPage(currentPage + 1)}
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
