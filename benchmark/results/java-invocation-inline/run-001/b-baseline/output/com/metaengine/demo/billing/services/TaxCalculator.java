package com.metaengine.demo.billing.services;

import com.metaengine.demo.billing.aggregates.Invoice;
import java.util.List;

/** Domain service that computes tax amounts for invoices. */
public class TaxCalculator {
    /** Create an invoice with calculated tax from the partial input. */
    public Invoice create(Invoice input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find a tax-calculated invoice by id. Returns null when not found. */
    public Invoice findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to {@code limit} tax-calculated invoices. */
    public List<Invoice> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Remove tax calculation for the given id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
