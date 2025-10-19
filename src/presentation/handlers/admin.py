"""
Admin handlers
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from loguru import logger

from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.payment_repository import PaymentRepository
from src.domain.repositories.test_repository import TestRepository
from src.infrastructure.database.session import get_db_session
from src.infrastructure.database.repositories.user_repository import SQLAlchemyUserRepository
from src.infrastructure.database.repositories.payment_repository import SQLAlchemyPaymentRepository
from src.infrastructure.database.repositories.test_repository import SQLAlchemyTestRepository
from src.presentation.keyboards.inline import back_to_menu_keyboard
from src.utils.helpers import format_price_kopecks, format_user_display_name

router = Router()


def is_admin(user: User, admin_ids: list[int]) -> bool:
    """Проверка, является ли пользователь администратором"""
    return user and user.is_admin


@router.message(Command("admin"))
async def admin_command(message: Message, user: User):
    """Команда /admin"""
    try:
        if not is_admin(user, []):
            await message.answer("❌ У вас нет прав администратора")
            return
        
        await message.answer(
            "👨‍💼 Панель администратора\n\n"
            "Доступные команды:\n"
            "/stats - Статистика бота\n"
            "/users - Список пользователей\n"
            "/payments - Статистика платежей\n"
            "/tests - Статистика тестов\n"
            "/broadcast - Рассылка сообщений\n"
            "/block <user_id> - Заблокировать пользователя\n"
            "/unblock <user_id> - Разблокировать пользователя"
        )
        
    except Exception as e:
        logger.error(f"Error in admin command: {e}")
        await message.answer("Произошла ошибка")


@router.message(Command("stats"))
async def admin_stats(message: Message, user: User):
    """Статистика бота"""
    try:
        if not is_admin(user, []):
            await message.answer("❌ У вас нет прав администратора")
            return
        
        async with get_db_session() as session:
            user_repository = SQLAlchemyUserRepository(session)
            payment_repository = SQLAlchemyPaymentRepository(session)
            test_repository = SQLAlchemyTestRepository(session)
            
            # Получаем статистику
            total_users = await user_repository.get_users_count()
            active_users = await user_repository.get_active_users(limit=1000)
            
            # Статистика платежей
            paid_orders = await payment_repository.get_orders_by_status("paid")
            total_revenue = sum(order.amount_kopecks for order in paid_orders)
            
            # Статистика тестов
            test_stats = await test_repository.get_test_statistics()
            
            await message.answer(
                f"📊 Статистика бота\n\n"
                f"👥 Пользователи:\n"
                f"• Всего: {total_users}\n"
                f"• Активных: {len(active_users)}\n\n"
                f"💳 Платежи:\n"
                f"• Успешных: {len(paid_orders)}\n"
                f"• Общая выручка: {format_price_kopecks(total_revenue)}\n\n"
                f"🧠 Тесты:\n"
                f"• Всего пройдено: {test_stats['total_tests']}\n"
                f"• Пройдено успешно: {test_stats['passed_tests']}\n"
                f"• Процент успеха: {test_stats['pass_rate']:.1f}%\n"
                f"• Средний балл: {test_stats['avg_score']:.1f}",
                reply_markup=back_to_menu_keyboard()
            )
        
    except Exception as(as e:
        logger.error(f"Error in admin_stats: {e}")
        await message.answer("Произошла ошибка при получении статистики")


@router.message(Command("users"))
async def admin_users(message: Message, user: User):
    """Список пользователей"""
    try:
        if not is_admin(user, []):
            await message.answer("❌ У вас нет прав администратора")
            return
        
        async with get_db_session() as session:
            user_repository = SQLAlchemyUserRepository(session)
            
            # Получаем активных пользователей
            active_users = await user_repository.get_active_users(limit=20)
            
            users_text = "👥 Последние пользователи:\n\n"
            for i, db_user in enumerate(active_users[:10], 1):
                display_name = format_user_display_name(
                    db_user.first_name, 
                    db_user.last_name, 
                    db_user.username
                )
                status = "✅" if not db_user.is_blocked else "❌"
                users_text += f"{i}. {status} {display_name} (ID: {db_user.telegram_id})\n"
            
            if len(active_users) > 10:
                users_text += f"\n... и еще {len(active_users) - 10} пользователей"
            
            await message.answer(users_text, reply_markup=back_to_menu_keyboard())
        
    except Exception as e:
        logger.error(f"Error in admin_users: {e}")
        await message.answer("Произошла ошибка при получении списка пользователей")


@router.message(Command("payments"))
async def admin_payments(message: Message, user: User):
    """Статистика платежей"""
    try:
        if not is_admin(user, []):
            await message.answer("❌ У вас нет прав администратора")
            return
        
        async with get_db_session() as session:
            payment_repository = SQLAlchemyPaymentRepository(session)
            
            # Получаем статистику по статусам
            paid_orders = await payment_repository.get_orders_by_status("paid")
            pending_orders = await payment_repository.get_orders_by_status("pending")
            failed_orders = await payment_repository.get_orders_by_status("failed")
            
            total_revenue = sum(order.amount_kopecks for order in paid_orders)
            
            await message.answer(
                f"💳 Статистика платежей\n\n"
                f"✅ Оплачено: {len(paid_orders)}\n"
                f"⏳ В ожидании: {len(pending_orders)}\n"
                f"❌ Неудачных: {len(failed_orders)}\n\n"
                f"💰 Общая выручка: {format_price_kopecks(total_revenue)}\n\n"
                f"📊 Последние платежи:\n"
                + "\n".join([
                    f"• {format_price_kopecks(order.amount_kopecks)} - {order.status}"
                    for order in paid_orders[:5]
                ]),
                reply_markup=back_to_menu_keyboard()
            )
        
    except Exception as e:
        logger.error(f"Error in admin_payments: {e}")
        await message.answer("Произошла ошибка при получении статистики платежей")


@router.message(Command("tests"))
async def admin_tests(message: Message, user: User):
    """Статистика тестов"""
    try:
        if not is_admin(user, []):
            await message.answer("❌ У вас нет прав администратора")
            return
        
        async with get_db_session() as session:
            test_repository = SQLAlchemyTestRepository(session)
            
            test_stats = await test_repository.get_test_statistics()
            
            await message.answer(
                f"🧠 Статистика тестов\n\n"
                f"📊 Общая статистика:\n"
                f"• Всего тестов: {test_stats['total_tests']}\n"
                f"• Пройдено успешно: {test_stats['passed_tests']}\n"
                f"• Не пройдено: {test_stats['failed_tests']}\n"
                f"• Процент успеха: {test_stats['pass_rate']:.1f}%\n"
                f"• Средний балл: {test_stats['avg_score']:.1f}\n"
                f"• Уникальных пользователей: {test_stats['unique_users']}\n\n"
                f"📈 Распределение по баллам:\n"
                + "\n".join([
                    f"• {score} баллов: {count} раз"
                    for score, count in sorted(test_stats['score_distribution'].items())
                ]),
                reply_markup=back_to_menu_keyboard()
            )
        
    except Exception as e:
        logger.error(f"Error in admin_tests: {e}")
        await message.answer("Произошла ошибка при получении статистики тестов")


@router.message(Command("block"))
async def admin_block_user(message: Message, user: User):
    """Заблокировать пользователя"""
    try:
        if not is_admin(user, []):
            await message.answer("❌ У вас нет прав администратора")
            return
        
        # Извлекаем user_id из команды
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("Использование: /block <user_id>")
            return
        
        try:
            target_user_id = int(parts[1])
        except ValueError:
            await message.answer("❌ Неверный формат user_id")
            return
        
        async with get_db_session() as session:
            user_repository = SQLAlchemyUserRepository(session)
            
            success = await user_repository.block_user(target_user_id)
            
            if success:
                await message.answer(f"✅ Пользователь {target_user_id} заблокирован")
                logger.info(f"User {target_user_id} blocked by admin {user.telegram_id}")
            else:
                await message.answer(f"❌ Пользователь {target_user_id} не найден")
        
    except Exception as e:
        logger.error(f"Error in admin_block_user: {e}")
        await message.answer("Произошла ошибка при блокировке пользователя")


@router.message(Command("unblock"))
async def admin_unblock_user(message: Message, user: User):
    """Разблокировать пользователя"""
    try:
        if not is_admin(user, []):
            await message.answer("❌ У вас нет прав администратора")
            return
        
        # Извлекаем user_id из команды
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("Использование: /unblock <user_id>")
            return
        
        try:
            target_user_id = int(parts[1])
        except ValueError:
            await message.answer("❌ Неверный формат user_id")
            return
        
        async with get_db_session() as session:
            user_repository = SQLAlchemyUserRepository(session)
            
            success = await user_repository.unblock_user(target_user_id)
            
            if success:
                await message.answer(f"✅ Пользователь {target_user_id} разблокирован")
                logger.info(f"User {target_user_id} unblocked by admin {user.telegram_id}")
            else:
                await message.answer(f"❌ Пользователь {target_user_id} не найден")
        
    except Exception as e:
        logger.error(f"Error in admin_unblock_user: {e}")
        await message.answer("Произошла ошибка при разблокировке пользователя")
