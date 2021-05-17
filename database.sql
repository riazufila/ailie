--
-- PostgreSQL database dump
--

-- Dumped from database version 13.2
-- Dumped by pg_dump version 13.2

-- Started on 2021-05-17 21:32:09 +08

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 3085 (class 1262 OID 19678)
-- Name: ailie; Type: DATABASE; Schema: -; Owner: riazufila
--

CREATE DATABASE ailie WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'en_US.UTF-8';


ALTER DATABASE ailie OWNER TO riazufila;

\connect ailie

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 200 (class 1259 OID 19679)
-- Name: equipments; Type: TABLE; Schema: public; Owner: riazufila
--

CREATE TABLE public.equipments (
    equip_id bigint NOT NULL,
    equip_name text NOT NULL,
    equip_star integer NOT NULL,
    equip_exclusive boolean NOT NULL,
    equip_pickup boolean DEFAULT false NOT NULL,
    equip_stats json,
    equip_buffs json,
    equip_skill json,
    equip_instant_triggers json,
    equip_triggers json
);


ALTER TABLE public.equipments OWNER TO riazufila;

--
-- TOC entry 201 (class 1259 OID 19686)
-- Name: equipments_acquired; Type: TABLE; Schema: public; Owner: riazufila
--

CREATE TABLE public.equipments_acquired (
    equip_acquired_id bigint NOT NULL,
    equip_id bigint NOT NULL,
    inventory_id bigint NOT NULL,
    equip_acquired_exp bigint DEFAULT 0 NOT NULL,
    equip_acquired_limit_break integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.equipments_acquired OWNER TO riazufila;

--
-- TOC entry 202 (class 1259 OID 19691)
-- Name: equipments_acquired_equip_acquired_id_seq; Type: SEQUENCE; Schema: public; Owner: riazufila
--

ALTER TABLE public.equipments_acquired ALTER COLUMN equip_acquired_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.equipments_acquired_equip_acquired_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 203 (class 1259 OID 19693)
-- Name: equipments_equip_id_seq; Type: SEQUENCE; Schema: public; Owner: riazufila
--

ALTER TABLE public.equipments ALTER COLUMN equip_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.equipments_equip_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 204 (class 1259 OID 19695)
-- Name: guardians; Type: TABLE; Schema: public; Owner: riazufila
--

CREATE TABLE public.guardians (
    guardian_id bigint NOT NULL,
    guardian_username text,
    guild_id bigint,
    guardian_position text,
    guardian_gems bigint DEFAULT 0 NOT NULL,
    guardian_trophy bigint DEFAULT 0 NOT NULL,
    guardian_summon_count integer DEFAULT 0 NOT NULL,
    guardian_wins integer DEFAULT 0 NOT NULL,
    guardian_losses integer DEFAULT 0 NOT NULL,
    guardian_hourly timestamp with time zone,
    guardian_daily timestamp with time zone,
    guardian_daily_count integer DEFAULT 0 NOT NULL,
    guardian_exp bigint DEFAULT 0 NOT NULL,
    guardian_gambled_gems bigint DEFAULT 0 NOT NULL,
    guardian_spent_gems bigint DEFAULT 0 NOT NULL,
    guardian_won_gambled_gems bigint DEFAULT 0 NOT NULL,
    guardian_won_gambled_count bigint DEFAULT 0 NOT NULL,
    guardian_lose_gambled_gems bigint DEFAULT 0 NOT NULL,
    guardian_lose_gambled_count bigint DEFAULT 0 NOT NULL,
    guardian_gamble_count integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.guardians OWNER TO riazufila;

--
-- TOC entry 205 (class 1259 OID 19715)
-- Name: guilds; Type: TABLE; Schema: public; Owner: riazufila
--

CREATE TABLE public.guilds (
    guild_id bigint NOT NULL,
    guild_name text NOT NULL
);


ALTER TABLE public.guilds OWNER TO riazufila;

--
-- TOC entry 206 (class 1259 OID 19721)
-- Name: heroes; Type: TABLE; Schema: public; Owner: riazufila
--

CREATE TABLE public.heroes (
    hero_id bigint NOT NULL,
    hero_name text NOT NULL,
    hero_star integer NOT NULL,
    hero_pickup boolean DEFAULT false NOT NULL,
    equip_id bigint,
    hero_stats json,
    hero_buffs json,
    hero_skill json,
    hero_triggers json
);


ALTER TABLE public.heroes OWNER TO riazufila;

--
-- TOC entry 207 (class 1259 OID 19728)
-- Name: heroes_acquired; Type: TABLE; Schema: public; Owner: riazufila
--

CREATE TABLE public.heroes_acquired (
    hero_acquired_id bigint NOT NULL,
    hero_id bigint NOT NULL,
    inventory_id bigint NOT NULL,
    hero_acquired_exp bigint DEFAULT 0 NOT NULL,
    hero_acquired_limit_break integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.heroes_acquired OWNER TO riazufila;

--
-- TOC entry 208 (class 1259 OID 19733)
-- Name: heroes_acquired_hero_acquired_id_seq; Type: SEQUENCE; Schema: public; Owner: riazufila
--

ALTER TABLE public.heroes_acquired ALTER COLUMN hero_acquired_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.heroes_acquired_hero_acquired_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 209 (class 1259 OID 19735)
-- Name: heroes_hero_id_seq; Type: SEQUENCE; Schema: public; Owner: riazufila
--

ALTER TABLE public.heroes ALTER COLUMN hero_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.heroes_hero_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 210 (class 1259 OID 19737)
-- Name: inventories; Type: TABLE; Schema: public; Owner: riazufila
--

CREATE TABLE public.inventories (
    inventory_id bigint NOT NULL,
    guardian_id bigint NOT NULL
);


ALTER TABLE public.inventories OWNER TO riazufila;

--
-- TOC entry 211 (class 1259 OID 19740)
-- Name: inventories_inventory_id_seq; Type: SEQUENCE; Schema: public; Owner: riazufila
--

ALTER TABLE public.inventories ALTER COLUMN inventory_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.inventories_inventory_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 213 (class 1259 OID 19795)
-- Name: items; Type: TABLE; Schema: public; Owner: riazufila
--

CREATE TABLE public.items (
    item_id bigint NOT NULL,
    item_name text NOT NULL,
    item_price integer NOT NULL,
    item_description text
);


ALTER TABLE public.items OWNER TO riazufila;

--
-- TOC entry 215 (class 1259 OID 19805)
-- Name: items_acquired; Type: TABLE; Schema: public; Owner: riazufila
--

CREATE TABLE public.items_acquired (
    item_acquired_id bigint NOT NULL,
    item_id bigint NOT NULL,
    inventory_id bigint NOT NULL,
    item_acquired_quantity bigint DEFAULT 0 NOT NULL
);


ALTER TABLE public.items_acquired OWNER TO riazufila;

--
-- TOC entry 214 (class 1259 OID 19803)
-- Name: items_acquired_item_acquired_id_seq; Type: SEQUENCE; Schema: public; Owner: riazufila
--

ALTER TABLE public.items_acquired ALTER COLUMN item_acquired_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.items_acquired_item_acquired_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 212 (class 1259 OID 19793)
-- Name: items_item_id_seq; Type: SEQUENCE; Schema: public; Owner: riazufila
--

ALTER TABLE public.items ALTER COLUMN item_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.items_item_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 2926 (class 2606 OID 19743)
-- Name: equipments_acquired equipments_acquired_pkey; Type: CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.equipments_acquired
    ADD CONSTRAINT equipments_acquired_pkey PRIMARY KEY (equip_acquired_id);


--
-- TOC entry 2924 (class 2606 OID 19745)
-- Name: equipments equipments_pkey; Type: CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.equipments
    ADD CONSTRAINT equipments_pkey PRIMARY KEY (equip_id);


--
-- TOC entry 2928 (class 2606 OID 19747)
-- Name: guardians guardians_pkey; Type: CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.guardians
    ADD CONSTRAINT guardians_pkey PRIMARY KEY (guardian_id);


--
-- TOC entry 2930 (class 2606 OID 19749)
-- Name: guilds guilds_pkey; Type: CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.guilds
    ADD CONSTRAINT guilds_pkey PRIMARY KEY (guild_id);


--
-- TOC entry 2934 (class 2606 OID 19751)
-- Name: heroes_acquired heroes_acquired_pkey; Type: CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.heroes_acquired
    ADD CONSTRAINT heroes_acquired_pkey PRIMARY KEY (hero_acquired_id);


--
-- TOC entry 2932 (class 2606 OID 19753)
-- Name: heroes heroes_pkey; Type: CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.heroes
    ADD CONSTRAINT heroes_pkey PRIMARY KEY (hero_id);


--
-- TOC entry 2936 (class 2606 OID 19755)
-- Name: inventories inventories_pkey; Type: CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.inventories
    ADD CONSTRAINT inventories_pkey PRIMARY KEY (inventory_id);


--
-- TOC entry 2940 (class 2606 OID 19810)
-- Name: items_acquired items_acquired_pkey; Type: CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.items_acquired
    ADD CONSTRAINT items_acquired_pkey PRIMARY KEY (item_acquired_id);


--
-- TOC entry 2938 (class 2606 OID 19802)
-- Name: items items_pkey; Type: CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_pkey PRIMARY KEY (item_id);


--
-- TOC entry 2941 (class 2606 OID 19756)
-- Name: equipments_acquired equipments_equip_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.equipments_acquired
    ADD CONSTRAINT equipments_equip_id_fkey FOREIGN KEY (equip_id) REFERENCES public.equipments(equip_id);


--
-- TOC entry 2944 (class 2606 OID 19761)
-- Name: heroes equipments_equip_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.heroes
    ADD CONSTRAINT equipments_equip_id_fkey FOREIGN KEY (equip_id) REFERENCES public.equipments(equip_id) NOT VALID;


--
-- TOC entry 2947 (class 2606 OID 19766)
-- Name: inventories guardians_guardian_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.inventories
    ADD CONSTRAINT guardians_guardian_id_fkey FOREIGN KEY (guardian_id) REFERENCES public.guardians(guardian_id) NOT VALID;


--
-- TOC entry 2943 (class 2606 OID 19771)
-- Name: guardians guilds_guild_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.guardians
    ADD CONSTRAINT guilds_guild_id_fkey FOREIGN KEY (guild_id) REFERENCES public.guilds(guild_id) NOT VALID;


--
-- TOC entry 2945 (class 2606 OID 19776)
-- Name: heroes_acquired heroes_hero_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.heroes_acquired
    ADD CONSTRAINT heroes_hero_id_fkey FOREIGN KEY (hero_id) REFERENCES public.heroes(hero_id);


--
-- TOC entry 2946 (class 2606 OID 19781)
-- Name: heroes_acquired inventories_inventory_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.heroes_acquired
    ADD CONSTRAINT inventories_inventory_id_fkey FOREIGN KEY (inventory_id) REFERENCES public.inventories(inventory_id) NOT VALID;


--
-- TOC entry 2942 (class 2606 OID 19786)
-- Name: equipments_acquired inventories_inventory_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.equipments_acquired
    ADD CONSTRAINT inventories_inventory_id_fkey FOREIGN KEY (inventory_id) REFERENCES public.inventories(inventory_id) NOT VALID;


--
-- TOC entry 2948 (class 2606 OID 19811)
-- Name: items_acquired inventories_inventory_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.items_acquired
    ADD CONSTRAINT inventories_inventory_id_fkey FOREIGN KEY (inventory_id) REFERENCES public.inventories(inventory_id) NOT VALID;


--
-- TOC entry 2949 (class 2606 OID 19816)
-- Name: items_acquired items_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.items_acquired
    ADD CONSTRAINT items_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(item_id) NOT VALID;


-- Completed on 2021-05-17 21:32:09 +08

--
-- PostgreSQL database dump complete
--

