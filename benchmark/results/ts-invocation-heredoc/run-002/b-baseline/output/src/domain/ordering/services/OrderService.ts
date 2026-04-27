import { Order } from "../aggregates/Order";

/** Application service exposing order use cases. */
export class OrderService {
  create(input: Partial<Order>): Order {
    void input;
    throw new Error("not implemented");
  }

  findById(id: string): Order | null {
    void id;
    throw new Error("not implemented");
  }

  list(limit: number): Order[] {
    void limit;
    throw new Error("not implemented");
  }

  delete(id: string): void {
    void id;
    throw new Error("not implemented");
  }
}
