package com.metaengine.demo.catalog.services;

import com.metaengine.demo.catalog.aggregates.Product;
import java.util.List;

/** Pricing computation service for the Product aggregate. */
public class PricingEngine {

    /** Create a new Product with computed pricing from a partial input. */
    public Product create(Product input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a Product by id; returns null if not found. */
    public Product findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List Products, capped at the supplied limit. */
    public List<Product> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a Product by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
