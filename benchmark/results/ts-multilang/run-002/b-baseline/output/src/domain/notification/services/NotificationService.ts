import { Notification } from "../aggregates/Notification.js";

/** NotificationService domain service. */
export class NotificationService {
  create(input: Partial<Notification>): Notification {
    void input;
    throw new Error("not implemented");
  }

  findById(id: string): Notification | null {
    void id;
    throw new Error("not implemented");
  }

  list(limit: number): Notification[] {
    void limit;
    throw new Error("not implemented");
  }

  delete(id: string): void {
    void id;
    throw new Error("not implemented");
  }
}
