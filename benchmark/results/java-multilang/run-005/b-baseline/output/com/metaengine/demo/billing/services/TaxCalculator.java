package com.metaengine.demo.billing.services;

import com.metaengine.demo.billing.aggregates.Invoice;
import java.util.List;

/** TaxCalculator service for the billing domain. */
public class TaxCalculator {

    /** Create a new Invoice. */
    public Invoice create(Invoice input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find an Invoice by id. May return null. */
    public Invoice findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List invoices up to the given limit. */
    public List<Invoice> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete an Invoice by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
