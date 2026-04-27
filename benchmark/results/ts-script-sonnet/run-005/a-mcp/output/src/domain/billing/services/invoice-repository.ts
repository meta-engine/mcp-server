import { Invoice } from '../aggregates/invoice';

export class InvoiceRepository {

  create(input: Partial<Invoice>): Invoice { throw new Error('not implemented'); }

  findById(id: string): Invoice | null { throw new Error('not implemented'); }

  list(limit: number): Invoice[] { throw new Error('not implemented'); }

  delete(id: string): void { throw new Error('not implemented'); }
}
