from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib import colors


def simulate_minute_by_minute_with_idle_tracking_landscape():
    import random

    random.seed(42)

    able_ranges = {(0, 29): 2, (30, 57): 3, (58, 82): 4, (83, 99): 5}
    baker_ranges = {(0, 34): 3, (35, 59): 4, (60, 79): 5, (80, 99): 6}
    iat_ranges = {(0, 24): 1, (25, 64): 2, (65, 84): 3, (85, 99): 4}
    iat_random = [
        26,
        98,
        90,
        26,
        42,
        74,
        80,
        68,
        22,
        48,
        34,
        45,
        24,
        34,
        63,
        38,
        80,
        42,
        56,
        89,
        18,
        51,
        71,
        16,
        92,
        1,
    ]
    service_random = [
        95,
        21,
        51,
        92,
        89,
        38,
        13,
        61,
        50,
        49,
        39,
        53,
        88,
        1,
        81,
        53,
        81,
        64,
        1,
        67,
        1,
        47,
        75,
        57,
        87,
        47,
    ]

    class Worker:
        def __init__(self, name: str, ranges: dict[tuple[int, int], int]) -> None:
            self.name = name
            self.free = True
            self.work_left = 0
            self.ranges = ranges
            self.idle_time = 0
            self.state_changed = False

        def get_work_time(self, random_num: int) -> int:
            for (start, end), work_time in self.ranges.items():
                if start <= random_num <= end:
                    return work_time
            return 0

        def start_work(self, random_num: int) -> None:
            self.work_left = self.get_work_time(random_num)
            if self.work_left != 0:
                self.free = False
                self.state_changed = True

        def tick(self) -> None:
            self.state_changed = False
            if self.free:
                self.idle_time += 1
            else:
                self.work_left -= 1
                if self.work_left <= 0:
                    self.work_left = 0
                    self.state_changed = True
                    self.free = True

    class Customer:
        def __init__(self, id: int, ranges: dict[tuple[int, int], int]) -> None:
            self.id = id
            self.ranges = ranges
            self.arrival_time = 0
            self.iat = 0

        def get_interarrival_time(self, random_num: int) -> int:
            for (start, end), inter_time in self.ranges.items():
                if start <= random_num <= end:
                    return inter_time
            return 0

        def schedule_next(self, current_time: int, random_num: int) -> int:
            self.iat = self.get_interarrival_time(random_num)
            self.arrival_time = current_time + self.iat
            return self.arrival_time

    able = Worker("Able", able_ranges)
    baker = Worker("Baker", baker_ranges)

    data = [
        [
            "Minute",
            "Customer",
            "Random IAT",
            "IAT",
            "Arrival Time",
            "Worker",
            "Random Service",
            "Service Time",
            "Service Start",
            "Service End",
            "Able Idle Time",
            "Baker Idle Time",
        ]
    ]

    customers = []
    waiting_queue = []

    for minute in range(6000):
        cust = Customer(len(customers) + 1, iat_ranges)
        random_iat = random.randint(0, 99)
        cust.schedule_next(minute, random_iat)
        customers.append(cust)

        for c in customers:
            if c.arrival_time == minute:
                waiting_queue.append(c)

        for w in (able, baker):
            w.tick()

        able_idle_display = ""
        baker_idle_display = ""

        if waiting_queue:
            if baker.free:
                worker = baker
            elif able.free:
                worker = able
            else:
                worker = None

            if worker:
                c = waiting_queue.pop(0)
                random_service = random.randint(0, 99)
                service_time = worker.get_work_time(random_service)
                worker.start_work(random_service)
                service_start = minute
                service_end = minute + service_time

                if worker.idle_time > 0:
                    if worker.name == "Able":
                        able_idle_display = worker.idle_time
                    else:
                        baker_idle_display = worker.idle_time
                    worker.idle_time = 0

                data.append(
                    [
                        minute,
                        f"C{c.id}",
                        random_iat,
                        c.iat,
                        c.arrival_time,
                        worker.name,
                        random_service,
                        service_time,
                        service_start,
                        service_end,
                        able_idle_display,
                        baker_idle_display,
                    ]
                )

    pdf_path = "./simulation_minute_by_minute_idle_landscape_random.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=landscape(letter))
    table = Table(data, repeatRows=1)

    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ]
    )
    table.setStyle(style)

    doc.build([table, Spacer(1, 12)])
    return pdf_path


pdf_path = simulate_minute_by_minute_with_idle_tracking_landscape()
print(pdf_path)

