import { CheckoutSession } from "../value-objects/CheckoutSession";
import { Id } from "../../../shared/value-objects/Id";

/** DiscountService service. */
export class DiscountService {
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
