package com.metaengine.demo.catalog.services;

import com.metaengine.demo.catalog.aggregates.Product;
import java.util.List;

/** ProductRepository persistence service in the catalog domain. */
public class ProductRepository {
    /** Persist a new Product from a partial input. */
    public Product create(Product input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a Product by id, or null if not found. */
    public Product findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List Products up to limit. */
    public List<Product> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a Product by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
