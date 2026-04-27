package com.metaengine.demo.catalog.services;

import com.metaengine.demo.catalog.aggregates.Product;
import java.util.List;

/** Persistence gateway for catalog products. */
public class ProductRepository {
    /** Persist a new product from the provided partial input. */
    public Product create(Product input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Load a product by id. Returns null when not found. */
    public Product findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to {@code limit} products. */
    public List<Product> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Remove a product by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
