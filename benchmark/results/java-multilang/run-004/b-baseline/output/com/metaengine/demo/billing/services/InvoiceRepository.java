package com.metaengine.demo.billing.services;

import java.util.List;

import com.metaengine.demo.billing.aggregates.Invoice;

/** InvoiceRepository persistence service. */
public class InvoiceRepository {

    /** Persist an Invoice from a partial input. */
    public Invoice create(Invoice input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find an Invoice by id (may return null). */
    public Invoice findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List invoices up to limit. */
    public List<Invoice> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete an Invoice by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
