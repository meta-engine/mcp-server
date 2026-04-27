package com.metaengine.demo.catalog.services;

import com.metaengine.demo.catalog.aggregates.Product;
import java.util.List;

/** PricingEngine for the catalog domain. */
public class PricingEngine {

    /** Create a new Product with pricing applied. */
    public Product create(Product input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a Product by id; may return null. */
    public Product findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List products up to the given limit. */
    public List<Product> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete a product by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
