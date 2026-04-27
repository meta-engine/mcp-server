import { Invoice } from "../aggregates/Invoice";

/** Application service exposing invoice use cases. */
export class InvoiceService {
  create(input: Partial<Invoice>): Invoice {
    void input;
    throw new Error("not implemented");
  }

  findById(id: string): Invoice | null {
    void id;
    throw new Error("not implemented");
  }

  list(limit: number): Invoice[] {
    void limit;
    throw new Error("not implemented");
  }

  delete(id: string): void {
    void id;
    throw new Error("not implemented");
  }
}
