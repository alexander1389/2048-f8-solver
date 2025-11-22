import time

from collections import defaultdict


class Profiler:
    def __init__(self, enabled=True):
        self._enabled = enabled
        self._data = defaultdict(list)
        self._current_game_data = defaultdict(list)
        self._game_count = 0

    def start_timer(self, key):
        if not self._enabled:
            return
        self._current_game_data[key].append(time.time())

    def stop_timer(self, key):
        if not self._enabled:
            return
        if key in self._current_game_data and self._current_game_data[key]:
            start_time = self._current_game_data[key].pop()
            elapsed = time.time() - start_time
            self._current_game_data[key + '_time'].append(elapsed)

    def record_value(self, key, value):
        if not self._enabled:
            return
        self._current_game_data[key].append(value)

    def start_game(self):
        if not self._enabled:
            return
        self._current_game_data.clear()
        self._game_count += 1

    def end_game(self):
        if not self._enabled:
            return

        for key, values in self._current_game_data.items():
            if values:
                self._data[key].extend(values)

        self._current_game_data.clear()

    def get_summary(self):
        if not self._enabled:
            return {}

        summary = {}
        for key, values in self._data.items():
            if values:
                if 'time' in key:
                    summary[f'{key}_total'] = sum(values)
                    summary[f'{key}_avg'] = sum(values) / len(values)
                    summary[f'{key}_max'] = max(values)
                    summary[f'{key}_min'] = min(values)
                else:
                    summary[f'{key}_total'] = sum(values)
                    summary[f'{key}_avg'] = sum(values) / len(values)
                    summary[f'{key}_count'] = len(values)

        summary['games_played'] = self._game_count

        return summary

    def print_report(self, log_func=None):
        if not self._enabled:
            return

        summary = self.get_summary()
        if not summary:
            return

        report = ['=== PROFILING REPORT ===']

        timing_metrics = {}
        count_metrics = {}

        for key, value in summary.items():
            if 'time' in key:
                timing_metrics[key] = value
            else:
                count_metrics[key] = value

        report.append('\n--- TIMING STATISTICS (seconds) ---')
        for metric in sorted(timing_metrics.keys()):
            value = timing_metrics[metric]
            if 'total' in metric:
                report.append(f'{metric:30} {value:8.3f}s')
            else:
                report.append(f'{metric:30} {value:8.3f}s')

        report.append('\n--- COUNT STATISTICS ---')
        for metric in sorted(count_metrics.keys()):
            value = count_metrics[metric]
            if isinstance(value, float):
                report.append(f'{metric:30} {value:8.2f}')
            else:
                report.append(f'{metric:30} {value:8}')

        report.append('=' * 50)

        full_report = '\n'.join(report)

        if log_func:
            log_func(full_report)
        else:
            print(full_report)
