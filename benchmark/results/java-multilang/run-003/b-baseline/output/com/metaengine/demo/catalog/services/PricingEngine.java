package com.metaengine.demo.catalog.services;

import com.metaengine.demo.catalog.aggregates.Product;
import java.util.List;

/** PricingEngine domain service for the catalog domain. */
public class PricingEngine {
    /** Create a new Product from a partial input. */
    public Product create(Product input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a Product by its identifier. May return null. */
    public Product findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List Products up to the given limit. */
    public List<Product> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a Product by its identifier. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
