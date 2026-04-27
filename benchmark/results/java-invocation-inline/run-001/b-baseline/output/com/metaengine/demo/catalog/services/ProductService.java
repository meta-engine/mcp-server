package com.metaengine.demo.catalog.services;

import com.metaengine.demo.catalog.aggregates.Product;
import java.util.List;

/** Application service exposing catalog product operations. */
public class ProductService {
    /** Create a product from the provided partial input. */
    public Product create(Product input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a product by id. Returns null when not found. */
    public Product findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to {@code limit} products. */
    public List<Product> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a product by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
