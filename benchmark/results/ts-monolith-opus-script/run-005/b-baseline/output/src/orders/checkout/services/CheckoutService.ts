import { Id } from "../../../shared/value-objects/Id";
import { CheckoutSession } from "../value-objects/CheckoutSession";

/** CRUD operations on CheckoutSession value objects. */
export class CheckoutService {
  create(input: Partial<CheckoutSession>): CheckoutSession {
    void input;
    throw new Error("not implemented");
  }

  findById(id: Id): CheckoutSession | null {
    void id;
    throw new Error("not implemented");
  }

  list(limit: number): CheckoutSession[] {
    void limit;
    throw new Error("not implemented");
  }

  delete(id: Id): void {
    void id;
    throw new Error("not implemented");
  }
}
