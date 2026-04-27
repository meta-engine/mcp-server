import { Order } from "../aggregates/Order";
import { Id } from "../../shared/value-objects/Id";

/** CRUD operations for orders. */
export class OrderService {
  create(input: Partial<Order>): Order {
    void input;
    throw new Error("not implemented");
  }

  findById(id: Id): Order | null {
    void id;
    throw new Error("not implemented");
  }

  list(limit: number): Order[] {
    void limit;
    throw new Error("not implemented");
  }

  delete(id: Id): void {
    void id;
    throw new Error("not implemented");
  }
}
