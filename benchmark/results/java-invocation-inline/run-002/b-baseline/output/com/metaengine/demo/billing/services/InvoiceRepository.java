package com.metaengine.demo.billing.services;

import java.util.List;

import com.metaengine.demo.billing.aggregates.Invoice;

/** InvoiceRepository for the billing domain. */
public class InvoiceRepository {

    /** Persist a new Invoice from partial input. */
    public Invoice create(Invoice input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find an Invoice by id. Returns null if not found. */
    public Invoice findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List Invoices up to the given limit. */
    public List<Invoice> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete the Invoice with the given id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
