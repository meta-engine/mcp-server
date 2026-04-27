package com.metaengine.demo.billing.services;

import com.metaengine.demo.billing.aggregates.Invoice;
import java.util.List;

/** Persistence gateway for invoices. */
public class InvoiceRepository {
    /** Persist a new invoice from the provided partial input. */
    public Invoice create(Invoice input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Load an invoice by id. Returns null when not found. */
    public Invoice findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to {@code limit} invoices. */
    public List<Invoice> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Remove an invoice by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
