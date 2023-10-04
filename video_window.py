# External Libraries
import tkinter as tk
import cv2
from PIL import Image, ImageTk
import threading

# Local Modules
from lsl import get_speed_from_stream


class VideoPlaybackWindow(tk.Toplevel):
    def __init__(self, video_path, stream, parent):
        super().__init__()

        # Основные параметры
        self.parent = parent
        self.title("BrainStart")

        # Инициализация и размещение видео холста
        self.video_canvas = tk.Canvas(self, bg="black")
        self.video_canvas.pack(fill="both", expand=True)

        # Событие закрытия окна
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Инициализация скорости воспроизведения
        self.playback_speed = 1.0

        # Создание и размещение прямоугольников для отображения скорости
        self._create_speed_rectangles()

        # Сохранение ссылки на виджет
        self.parent.video_canvas = self.video_canvas

        # Параметры для потока обновления скорости
        self.is_running = True
        self.speed_thread = threading.Thread(target=self.update_speed, args=(stream,))
        self.speed_thread.daemon = True
        self.speed_thread.start()

        self.frame_delay = 1 # Задержка между кадрами

        # Запуск процесса воспроизведения видео
        self.play_video(video_path, stream)

    def _create_speed_rectangles(self):
        # Параметры прямоугольников
        self.rectangle_width = 30
        self.rectangle_height = 200
        self.fill_percentage = 0.5

        # Рисование прямоугольников
        self.outer_rectangle = self.video_canvas.create_rectangle(
            10, 10,
            10 + self.rectangle_width, 10 + self.rectangle_height,
            outline="white", width=2
        )
        self.inner_rectangle = self.video_canvas.create_rectangle(
            10, 10 + self.rectangle_height * self.fill_percentage,
                10 + self.rectangle_width, 10 + self.rectangle_height,
            fill="green"
        )

    def update_speed(self, stream):
        """Обновление скорости воспроизведения в потоке."""
        while self.is_running:
            new_speed = get_speed_from_stream(stream)
            if new_speed is not None:
                max_delay = 1000
                self.playback_speed = new_speed
                self.fill_percentage = new_speed / max_delay

                self.frame_delay = max(1, int(max_delay / self.playback_speed))
                print('Задержка между кадрами: ', self.frame_delay, 'мс.')

    def play_video(self, video_path, stream):
        """Запуск воспроизведения видео и создание элементов интерфейса."""
        self.cap = cv2.VideoCapture(video_path)  # Получаем видеопоток
        self.total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)  # Получаем общее количество кадров

        # Получаем первый кадр и создаем начальное изображение на холсте
        ret, frame = self.cap.read()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        im = Image.fromarray(frame_rgb)
        self.imgtk = ImageTk.PhotoImage(image=im)
        self.canvas_img = self.video_canvas.create_image(0, 0, anchor="nw", image=self.imgtk)

        # Создаем текстовый элемент для отображения процента просмотренного видео
        self.percentage_text = self.video_canvas.create_text(
            self.video_canvas.winfo_width() - 15,
            self.video_canvas.winfo_height() - 15,
            fill="white",
            anchor="se"
        )

        # Используется after для рекурсивного обновления кадров
        self.update_video_frame()

    def update_video_frame(self):
        """Обновление отображаемого кадра видео."""
        if not self.video_canvas.winfo_exists():
            self.cap.release()
            return

        ret, frame = self.cap.read()
        if not ret:
            self.cap.release()
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        canvas_width = self.video_canvas.winfo_width()
        canvas_height = self.video_canvas.winfo_height()
        im = Image.fromarray(frame_rgb).resize((canvas_width, canvas_height))
        imgtk = ImageTk.PhotoImage(image=im)

        self.video_canvas.itemconfig(self.canvas_img, image=imgtk)
        self.video_canvas.imgtk = imgtk

        current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        percentage = (current_frame / self.total_frames) * 100
        self.video_canvas.itemconfig(self.percentage_text, text=f"{percentage:.2f}%")

        # Обновление координат текста процентов
        self.video_canvas.coords(self.percentage_text,
                                 self.video_canvas.winfo_width() - 15,
                                 self.video_canvas.winfo_height() - 15)

        # Устанавливаем координаты прямоугольников поверх видео и слева
        rect_left = 10  # Фиксированный отступ слева
        rect_top = (canvas_height - self.rectangle_height) / 2
        rect_bottom = rect_top + self.rectangle_height

        self.video_canvas.coords(self.outer_rectangle,
                                 rect_left, rect_top,
                                 rect_left + self.rectangle_width, rect_bottom)

        inner_rect_top = rect_bottom - self.fill_percentage * self.rectangle_height

        self.video_canvas.coords(self.inner_rectangle,
                                 rect_left, inner_rect_top,
                                 rect_left + self.rectangle_width, rect_bottom)

        self.video_canvas.tag_raise(self.inner_rectangle)
        self.video_canvas.tag_raise(self.outer_rectangle)

        # Используем текущее значение скорости воспроизведения и вызываем функцию снова через after
        self.video_canvas.after(self.frame_delay, self.update_video_frame)

    def on_close(self):
        """Обработчик закрытия окна воспроизведения."""
        self.parent.video_canvas = None
        self.is_running = False
        self.destroy()
