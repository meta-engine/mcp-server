package com.metaengine.demo.catalog.services;

import java.util.List;

import com.metaengine.demo.catalog.aggregates.Product;

/** PricingEngine for the catalog domain. */
public class PricingEngine {

    /** Create a new Product from partial input. */
    public Product create(Product input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a Product by id. Returns null if not found. */
    public Product findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List Products up to the given limit. */
    public List<Product> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete the Product with the given id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
