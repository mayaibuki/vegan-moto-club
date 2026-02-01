"use client"

import { useState, useMemo } from "react"
import { Input } from "./ui/input"
import { Button } from "./ui/button"
import { ProductCard } from "./ProductCard"
import { Product } from "@/lib/notion"
import {
  filterProducts,
  getUniqueBrands,
  getUniqueCategories,
  getUniqueGenders,
  getUniqueRidingStyles,
} from "@/lib/utils"
import { Badge } from "./ui/badge"

interface ProductGridProps {
  products: Product[]
}

export function ProductGrid({ products }: ProductGridProps) {
  const [search, setSearch] = useState("")
  const [selectedBrand, setSelectedBrand] = useState<string | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [selectedGender, setSelectedGender] = useState<string | null>(null)
  const [selectedRidingStyle, setSelectedRidingStyle] = useState<string | null>(null)
  const [showFilters, setShowFilters] = useState(false)

  const brands = useMemo(() => getUniqueBrands(products), [products])
  const categories = useMemo(() => getUniqueCategories(products), [products])
  const genders = useMemo(() => getUniqueGenders(products), [products])
  const ridingStyles = useMemo(() => getUniqueRidingStyles(products), [products])

  const filteredProducts = useMemo(
    () =>
      filterProducts(products, {
        brand: selectedBrand || undefined,
        category: selectedCategory || undefined,
        gender: selectedGender || undefined,
        ridingStyle: selectedRidingStyle || undefined,
        search: search || undefined,
      }),
    [products, search, selectedBrand, selectedCategory, selectedGender, selectedRidingStyle]
  )

  const activeFilters = [
    selectedBrand,
    selectedCategory,
    selectedGender,
    selectedRidingStyle,
    search ? `Search: ${search}` : null,
  ].filter(Boolean)

  return (
    <div className="w-full">
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar Filters */}
        <aside
          className={`lg:w-64 flex-shrink-0 ${
            showFilters ? "block" : "hidden lg:block"
          }`}
        >
          <div className="space-y-6 sticky top-24">
            {/* Search */}
            <div>
              <h3 className="font-heading font-semibold mb-3">Search</h3>
              <Input
                placeholder="Search products..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>

            {/* Brand Filter */}
            <div>
              <h3 className="font-heading font-semibold mb-3">Brand</h3>
              <div className="space-y-2">
                <Button
                  variant={selectedBrand === null ? "default" : "outline"}
                  className="w-full justify-start"
                  onClick={() => setSelectedBrand(null)}
                  size="sm"
                >
                  All Brands
                </Button>
                {brands.map((brand) => (
                  <Button
                    key={brand}
                    variant={selectedBrand === brand ? "default" : "outline"}
                    className="w-full justify-start"
                    onClick={() => setSelectedBrand(brand)}
                    size="sm"
                  >
                    {brand}
                  </Button>
                ))}
              </div>
            </div>

            {/* Category Filter */}
            <div>
              <h3 className="font-heading font-semibold mb-3">Category</h3>
              <div className="space-y-2">
                <Button
                  variant={selectedCategory === null ? "default" : "outline"}
                  className="w-full justify-start"
                  onClick={() => setSelectedCategory(null)}
                  size="sm"
                >
                  All Categories
                </Button>
                {categories.map((category) => (
                  <Button
                    key={category}
                    variant={selectedCategory === category ? "default" : "outline"}
                    className="w-full justify-start"
                    onClick={() => setSelectedCategory(category)}
                    size="sm"
                  >
                    {category}
                  </Button>
                ))}
              </div>
            </div>

            {/* Gender Filter */}
            <div>
              <h3 className="font-heading font-semibold mb-3">Gender</h3>
              <div className="space-y-2">
                <Button
                  variant={selectedGender === null ? "default" : "outline"}
                  className="w-full justify-start"
                  onClick={() => setSelectedGender(null)}
                  size="sm"
                >
                  All Genders
                </Button>
                {genders.map((gender) => (
                  <Button
                    key={gender}
                    variant={selectedGender === gender ? "default" : "outline"}
                    className="w-full justify-start"
                    onClick={() => setSelectedGender(gender)}
                    size="sm"
                  >
                    {gender}
                  </Button>
                ))}
              </div>
            </div>

            {/* Riding Style Filter */}
            <div>
              <h3 className="font-heading font-semibold mb-3">Riding Style</h3>
              <div className="space-y-2">
                <Button
                  variant={selectedRidingStyle === null ? "default" : "outline"}
                  className="w-full justify-start"
                  onClick={() => setSelectedRidingStyle(null)}
                  size="sm"
                >
                  All Styles
                </Button>
                {ridingStyles.map((style) => (
                  <Button
                    key={style}
                    variant={selectedRidingStyle === style ? "default" : "outline"}
                    className="w-full justify-start"
                    onClick={() => setSelectedRidingStyle(style)}
                    size="sm"
                  >
                    {style}
                  </Button>
                ))}
              </div>
            </div>

            {/* Clear Filters */}
            {activeFilters.length > 0 && (
              <Button
                variant="outline"
                className="w-full"
                onClick={() => {
                  setSelectedBrand(null)
                  setSelectedCategory(null)
                  setSelectedGender(null)
                  setSelectedRidingStyle(null)
                  setSearch("")
                }}
              >
                Clear All Filters
              </Button>
            )}
          </div>
        </aside>

        {/* Main Content */}
        <div className="flex-1">
          {/* Toggle Filters Button (Mobile) */}
          <div className="mb-4 lg:hidden">
            <Button
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
              className="w-full"
            >
              {showFilters ? "Hide Filters" : "Show Filters"}
            </Button>
          </div>

          {/* Active Filters Display */}
          {activeFilters.length > 0 && (
            <div className="mb-6 p-4 bg-muted rounded-lg">
              <h3 className="text-sm font-semibold mb-2">Active Filters:</h3>
              <div className="flex flex-wrap gap-2">
                {activeFilters.map((filter, idx) => (
                  <Badge key={idx} variant="secondary">
                    {filter}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Products Grid */}
          <div>
            <p className="text-sm text-muted-foreground mb-4">
              Showing {filteredProducts.length} of {products.length} products
            </p>

            {filteredProducts.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-muted-foreground">No products found matching your filters.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredProducts.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
