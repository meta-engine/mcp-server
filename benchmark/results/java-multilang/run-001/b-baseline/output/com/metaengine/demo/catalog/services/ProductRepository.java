package com.metaengine.demo.catalog.services;

import java.util.List;

import com.metaengine.demo.catalog.aggregates.Product;

/** ProductRepository for the catalog domain. */
public class ProductRepository {

    /** Persists a new Product from the partial input. */
    public Product create(Product input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Finds a Product by id. May return null. */
    public Product findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Lists Products up to the given limit. */
    public List<Product> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Deletes the Product with the given id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
