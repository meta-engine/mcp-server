package com.metaengine.demo.catalog.services;

import java.util.List;
import com.metaengine.demo.catalog.aggregates.Product;

/** ProductService domain service. */
public class ProductService {
    /** Create a Product. */
    public Product create(Product input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a Product by id; returns null if not found. */
    public Product findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to limit Products. */
    public List<Product> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a Product by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
