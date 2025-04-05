import unittest
from unittest.mock import AsyncMock, patch
import redis_gamestate

class TestRedisGameState(unittest.IsolatedAsyncioTestCase):

    @patch("redis_gamestate.redis_client")
    async def test_set_and_get_game_state(self, mock_redis):
        mock_redis.get = AsyncMock(return_value=b'{"trust": 70}')
        mock_redis.set = AsyncMock(return_value=True)

        user_id = "test_user"
        state = {"trust": 70}
        await redis_gamestate.set_game_state(user_id, state)
        result = await redis_gamestate.get_game_state(user_id)

        self.assertEqual(result, {"trust": 70})
        mock_redis.set.assert_called_once()
        mock_redis.get.assert_called_once()

if __name__ == '__main__':
    unittest.main()
