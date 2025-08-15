from django.core.cache import cache
from django.utils import timezone
from rest_framework.throttling import BaseThrottle

class PlanDailyWithMinIntervalThrottle(BaseThrottle):
    cache_prefix = "throttle:plan"
    min_interval_seconds = 60  # не чаще 1/мин

    def allow_request(self, request, view):
        user = getattr(request, "user", None)
        # идентификатор: пользователь (или IP для анонима)
        if user and getattr(user, "is_authenticated", False):
            ident = f"user:{user.pk}"
            plan = getattr(user, "plan", None)
            daily_limit = getattr(plan, "messages_per_day", 1) if plan else 1
        else:
            ident = f"anon:{request.META.get('REMOTE_ADDR','0.0.0.0')}"
            daily_limit = 1  # анонимам: 1/сутки

        now = timezone.now()
        date_str = now.strftime("%Y-%m-%d")
        count_key = f"{self.cache_prefix}:{ident}:count:{date_str}"
        ts_key = f"{self.cache_prefix}:{ident}:ts"

        # правило "не чаще 1/мин"
        last_ts = cache.get(ts_key)  # храним float timestamp
        if last_ts is not None:
            elapsed = now.timestamp() - float(last_ts)
            if elapsed < self.min_interval_seconds:
                self._wait = int(self.min_interval_seconds - elapsed)
                return False

        # дневной лимит
        count = int(cache.get(count_key, 0))
        if count >= int(daily_limit):
            # ждать до полуночи
            midnight = (now + timezone.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            self._wait = int((midnight - now).total_seconds())
            return False

        # пропускаем: фиксируем событие
        cache.set(ts_key, now.timestamp(), timeout=24 * 3600)
        cache.set(count_key, count + 1, timeout=24 * 3600)
        self._wait = None
        return True

    def wait(self):
        return getattr(self, "_wait", None)