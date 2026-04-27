import { Invoice } from '../aggregates/Invoice';

/** TaxCalculator computes tax amounts applicable to invoices. */
export class TaxCalculator {
  create(input: Partial<Invoice>): Invoice {
    void input;
    throw new Error('not implemented');
  }

  findById(id: string): Invoice | null {
    void id;
    throw new Error('not implemented');
  }

  list(limit: number): Invoice[] {
    void limit;
    throw new Error('not implemented');
  }

  delete(id: string): void {
    void id;
    throw new Error('not implemented');
  }
}
